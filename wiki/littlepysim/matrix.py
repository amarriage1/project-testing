# -*- coding: utf-8 -*-
"""
Created on 2018-11-30

Contains all the code regarding usage of credit rating migration matrix

A migration matrix is a set of probabilities of transition from one rating to another, it is implemented as
 dictionary:
     * property name: the name of the matrix
     * property rating_scale_name : the name of the underlying rating scale. This name must be an existing key in
      a rating scale set structure
     * cells: a dictionary containing the cells of the matrix
         * key : source rating
         * value : a dictionary :
             * key : final rating
             * value: the probability (a float)


@author: dlemarchand
"""

import littlepysim.ratingscale as lp_rs



def apply_montecarlo_migration(scenario,bucket,prevBucket,migration_matrix_struct, rating_scale_set_struct, exposure, alea, stage_fct = None):
    """
    return a new exposure according to the alea
    """
    probabilities = []
    denotch_params = {}
    denotch_indicator = 0
    denotch_degradation = 0
    final_matrix = migration_matrix_struct
    
    #Adjust the rating, 
    all_ratings = lp_rs.list_ratings(rating_scale_set_struct, migration_matrix_struct['rating_scale_name'])
    rating_code = exposure['rating_code']
    if not rating_code in all_ratings:
        rating_code = rating_code.replace('+','').replace('-','').strip()
        if not rating_code in all_ratings:
            raise ValueError("Unknown rating {} => {} for rating scale : {}".format(exposure['rating_code'], rating_code,migration_matrix_struct['rating_scale_name']))
   
    #if denotch_fct:
    #    denotch_params = denotch_fct(scenario, bucket)
    #    denotch_indicator = denotch_params['denotch_indicator']
    #    denotch_degradation = denotch_params['degradation']
    #if ( denotch_indicator != 0) and denotch_degradation:
    #    final_matrix = lp_denotch.apply_denotching(denotch_params['denotch_indicator'],denotch_params['degradation'],denotch_params['pd_imposee'],
    #                                                 rating_scale_set_struct,migration_matrix_struct)

    is_non_performing = lp_rs.is_nonperforming(rating_scale_set_struct,final_matrix['rating_scale_name'],rating_code)
    if is_non_performing:
        probabilities = build_default_probabilities(final_matrix, rating_scale_set_struct, rating_code)
    else:
        probabilities = extract_probabilities(final_matrix, rating_scale_set_struct, rating_code)
    cumulated_edf = float(0)
    for i,probability in enumerate(probabilities):
        new_rating = probability[0]
        pd = probability[1]
        cumulated_edf = cumulated_edf + pd
        #calcul lgd
        #lgd_ifrs9, lgd_reg, lgd_pit = None, None, None
        #if(lgd_fct):
        #    lgdValues = lgd_fct(scenario,bucket,exposure)
        #    lgd_ifrs9 =lgdValues['lgd_ifrs9']
        #    lgd_reg =lgdValues['lgd_reg']
        #    lgd_pit = lgdValues['lgd_pit']
        
        #Floor S2
        floor_s2 = False
        if (exposure['stage']=='2'):
            if (lp_rs.compareRatings(new_rating,rating_code,rating_scale_set_struct,migration_matrix_struct['rating_scale_name']) <= 0):
                #dégradation
                floor_s2 = True

        if alea<=cumulated_edf or i == (len(probabilities)-1) :
            new_exposure = {}
            if stage_fct:
                s1, s2, s3 = stage_fct(new_rating, exposure['rating_code_origin'], rating_code, exposure['stage'])
                stage = ""
                if s3 >0:
                    stage = "3"
                else: 
                    if (floor_s2):    
                        s2 = s2 + s1
                        s1 = 0
                    if s1>s2 :
                        stage= "1"
                    else:
                        stage= "2"                    
                new_exposure={'rating_code': new_rating , 
                              'stage' : stage, 
                              'ead_reg' : exposure['ead_reg'], 
                              'lgd_ifrs9' : exposure['lgd_ifrs9'],
                              'lgd_reg' : exposure['lgd_reg'],
                              'lgd_pit' : exposure['lgd_pit'],
                              'previous_rating_code': rating_code, 
                              'previous_stage' : exposure['stage'],
                              'previous_lgd_ifrs9' : exposure['lgd_ifrs9'],
                              'previous_lgd_reg' : exposure['lgd_reg'],
                              'previous_lgd_pit' : exposure['lgd_pit'],
                              'rating_code_origin' : exposure['rating_code_origin']}
            else:
                new_exposure={'rating_code': new_rating , 
                              'stage' : exposure['stage'], 
                              'ead_reg' : exposure['ead_reg'], 
                              'lgd_ifrs9' : exposure['lgd_ifrs9'],
                              'lgd_reg' : exposure['lgd_reg'],
                              'lgd_pit' : exposure['lgd_pit'],
                              'previous_rating_code': rating_code, 
                              'previous_stage' : exposure['stage'],
                              'previous_lgd_ifrs9' : exposure['lgd_ifrs9'],
                              'previous_lgd_reg' : exposure['lgd_reg'],
                              'previous_lgd_pit' : exposure['lgd_pit'],
                              'rating_code_origin' : exposure['rating_code_origin']} 
            #ifrs9 computation
            #if ecl_fct:
            #    eclValues = ecl_fct(scenario,bucket,prevBucket,new_exposure)
            #    if eclValues:
            #        new_exposure['el_final'] = eclValues['elFinal']
            #    else:
            #        new_exposure['el_final'] = None
            return new_exposure
    raise ValueError("Sum(pd) < 1 {} {}".format(migration_matrix_struct['name'], rating_code ))        

def apply_analytic_migration(scenario, bucket, prevBucket, migration_matrix_struct, rating_scale_set_struct, exposure,stage_fct = None,denotched = False):    
    """
    return an array of exposure created by the usage of the migration matrix
    """
    probabilities = []
    denotch_params = {}
    denotch_indicator = 0
    final_matrix = migration_matrix_struct
    #Adjust the rating, 
    all_ratings = lp_rs.list_ratings(rating_scale_set_struct, migration_matrix_struct['rating_scale_name'])
    rating_code = exposure['rating_code']
    if not rating_code in all_ratings:
        rating_code = rating_code.replace('+','').replace('-','').strip()
        if not rating_code in all_ratings:
            raise ValueError("Unknown rating {} => {} for rating scale : {}".format(exposure['rating_code'], rating_code,migration_matrix_struct['rating_scale_name']))
            
    #if denotch_fct:
    #    denotch_params = denotch_fct(scenario, bucket)
    #    denotch_indicator = denotch_params['denotch_indicator']
    #    denotch_degradation = denotch_params['degradation']
    #if ( denotch_indicator != 0) and denotch_degradation:
    #    final_matrix = lp_denotch.apply_denotching(denotch_params['denotch_indicator'],denotch_params['degradation'],denotch_params['pd_imposee'],
    #                                                 rating_scale_set_struct,migration_matrix_struct)

    is_non_performing = lp_rs.is_nonperforming(rating_scale_set_struct,final_matrix['rating_scale_name'],rating_code)
    if is_non_performing:
        probabilities = build_default_probabilities(final_matrix, rating_scale_set_struct, rating_code)
    else:
        probabilities = extract_probabilities(final_matrix, rating_scale_set_struct, rating_code)
    exposures = []
    for probability in probabilities:
        new_exposure = {}
        new_rating = probability[0]
        pd = probability[1]
        #if abs(pd)>0:#0.000000001:            
        lgd_ifrs9, lgd_reg, lgd_pit = None, None, None
        #if(lgd_fct):
        #    lgdValues = lgd_fct(scenario,bucket,exposure)
        #    lgd_ifrs9 =lgdValues['lgd_ifrs9']
        #    lgd_reg =lgdValues['lgd_reg']
        #    lgd_pit = lgdValues['lgd_pit']

        #Floor S2
        floor_s2 = False
        if (exposure['stage']=='2'):
            if (lp_rs.compareRatings(new_rating,rating_code,rating_scale_set_struct,migration_matrix_struct['rating_scale_name']) <= 0):
                #dégradation
                floor_s2 = True

        if stage_fct:
            s1,s2,s3 = stage_fct(new_rating, exposure['rating_code_origin'], rating_code, exposure['stage'])
            ead_reg = pd * exposure['ead_reg']
            ead_s1 = ead_reg * s1
            ead_s2 = ead_reg * s2
            ead_s3 = ead_reg * s3
            if (floor_s2):                    
                ead_s2 = ead_s2 + ead_s1
                ead_s1 = 0.0
                s2 = s2 + s1
                s1 = 0

            if abs(s1)>0.00000000001:
                new_exposure={'rating_code': new_rating , 
                              'stage' : "1", 
                              'ead_reg' : ead_reg,
                              'ead_s1': ead_s1,
                              'ead_s2': ead_s2,
                              'ead_s3': ead_s3,
                              'lgd_ifrs9' : exposure['lgd_ifrs9'],
                              'lgd_reg' : exposure['lgd_reg'],
                              'lgd_pit' : exposure['lgd_pit'],
                              'previous_rating_code': rating_code, 
                              'previous_stage' : exposure['stage'],
                              'previous_lgd_ifrs9' : exposure['lgd_ifrs9'],
                              'previous_lgd_reg' : exposure['lgd_reg'],
                              'previous_lgd_pit' : exposure['lgd_pit'],
                              'rating_code_origin' : exposure['rating_code_origin']}

            if abs(s2)>0.00000000001:
                new_exposure={'rating_code': new_rating , 
                              'stage' : "2", 
                              'ead_reg' : ead_reg,
                              'ead_s1': ead_s1,
                              'ead_s2': ead_s2,
                              'ead_s3': ead_s3,
                              'lgd_ifrs9' : exposure['lgd_ifrs9'],
                              'lgd_reg' : exposure['lgd_reg'],
                              'lgd_pit' : exposure['lgd_pit'],
                              'previous_rating_code': rating_code, 
                              'previous_stage' : exposure['stage'],
                              'previous_lgd_ifrs9' : exposure['lgd_ifrs9'],
                              'previous_lgd_reg' : exposure['lgd_reg'],
                              'previous_lgd_pit' : exposure['lgd_pit'],
                              'rating_code_origin' : exposure['rating_code_origin']}

            if abs(s3)>0.00000000001:
                new_exposure={'rating_code': new_rating , 
                              'stage' : "3", 
                              'ead_reg' : ead_reg,
                              'ead_s1': ead_s1,
                              'ead_s2': ead_s2,
                              'ead_s3': ead_s3,
                              'lgd_ifrs9' : exposure['lgd_ifrs9'],
                              'lgd_reg' : exposure['lgd_reg'],
                              'lgd_pit' : exposure['lgd_pit'],
                              'previous_rating_code': rating_code, 
                              'previous_stage' : exposure['stage'],
                              'previous_lgd_ifrs9' : exposure['lgd_ifrs9'],
                              'previous_lgd_reg' : exposure['lgd_reg'],
                              'previous_lgd_pit' : exposure['lgd_pit'],
                              'rating_code_origin' : exposure['rating_code_origin']}

        else:                    
            new_exposure={'rating_code': new_rating , 
                          'stage' : None, 
                          'ead_reg' : pd * exposure['ead_reg'], 
                          'lgd_ifrs9' : exposure['lgd_ifrs9'],
                          'lgd_reg' : exposure['lgd_reg'],
                          'lgd_pit' : exposure['lgd_pit'],
                          'previous_rating_code': rating_code, 
                          'previous_stage' : exposure['stage'],
                          'previous_lgd_ifrs9' : exposure['lgd_ifrs9'],
                          'previous_lgd_reg' : exposure['lgd_reg'],
                          'previous_lgd_pit' : exposure['lgd_pit'],
                          'rating_code_origin' : exposure['rating_code_origin']}
        #ifrs9 computation
        #if ecl_fct:
        #    eclValues = ecl_fct(scenario,bucket,prevBucket,new_exposure)
        #    if eclValues:
        #        new_exposure['el_final'] = eclValues['elFinal']
        #    else:
        #        new_exposure['el_final'] = None
        if denotched:
            #up_date previous state to before denotching 
            new_exposure['previous_rating_code'] = exposure['previous_rating_code']
            new_exposure['previous_stage'] = exposure['previous_stage']
            new_exposure['previous_lgd_ifrs9'] = exposure['previous_lgd_ifrs9']
            new_exposure['previous_lgd_reg'] = exposure['previous_lgd_reg']
            new_exposure['previous_lgd_pit'] = exposure['previous_lgd_pit']
        exposures.append(new_exposure)    
    
    return exposures        
                                                                   
def find_probability(migration_matrix_struct, rating_from, rating_to):
    """
    return the probability for the transition rating_from => rating_to, default value is 0.0
    :param migration_matrix_struct: a dictionary
    :param rating_from: string
    :param rating_to: string
    :return: a float value
    """
    if rating_from in migration_matrix_struct['cells']:
        if rating_to in migration_matrix_struct['cells'][rating_from]:
            return migration_matrix_struct['cells'][rating_from][rating_to]
    return float(0)


def extract_probabilities(migration_matrix_struct, rating_scale_set_struct, rating_from):
    """
    return the rows of the matrix containing all the probabilities of transition for a rating
    :param migration_matrix_struct: a dictionary
    :param rating_scale_set_struct: a dictionary
    :param rating_from: string
    :return: an ordered array of tuple (rating, probability). The sort order is given by the rating scale
    """
    final_ratings = lp_rs.list_ratings(rating_scale_set_struct, migration_matrix_struct['rating_scale_name'])
    if final_ratings:
        probabilities = []
        for rating in final_ratings:
            probabilities.append((rating, find_probability(migration_matrix_struct, rating_from, rating)))
        return probabilities

def build_default_probabilities(migration_matrix_struct, rating_scale_set_struct, rating_default):
    """
    :return: an ordered array of tuple (rating, probability) corrresponding to the default rating
    """
    final_ratings = lp_rs.list_ratings(rating_scale_set_struct, migration_matrix_struct['rating_scale_name'])
    if final_ratings:
        probabilities = []
        for rating in final_ratings:
            if rating != rating_default:
                probabilities.append((rating, float(0)))
            else:
                probabilities.append((rating, float(1)))
        return probabilities

def build_rating_to_edf_struct(migration_matrix_struct,rating_scale_set_struct, method="default"):
    if method not in ["default", "aggregate"]:
        raise ValueError("Illegal method : {}".format(method))
    performing_ratings = lp_rs.list_ratings(rating_scale_set_struct,
                                               migration_matrix_struct['rating_scale_name'],
                                               "performing", "dict")
    nonperforming_ratings = lp_rs.list_ratings(rating_scale_set_struct,
                                                  migration_matrix_struct['rating_scale_name'],
                                                  "nonperforming", "dict")
    edf_list = []
    for rating in performing_ratings:
        pd = None
        if len(nonperforming_ratings) == 1:
            non_performing_rating = nonperforming_ratings[0]['rating_code']
            pd = find_probability(migration_matrix_struct, rating['rating_code'], non_performing_rating)
        else:
            if method == "default":
                # We use the worst non performing rating
                non_performing_rating = nonperforming_ratings[len(nonperforming_ratings) - 1]['rating_code']
                pd = find_probability(migration_matrix_struct, rating['rating_code'], non_performing_rating)
            if method == "aggregate":
                # We sum the probabilities of transition towards a nonperforming rating
                pd = float(0)
                for non_performing_rating in nonperforming_ratings:
                    pd = pd + find_probability(migration_matrix_struct,
                                               rating['rating_code'],
                                               non_performing_rating['rating_code'])
        item = rating.copy()
        item['edf'] = pd
        edf_list.append(item)
    # the last point
    item = nonperforming_ratings[len(nonperforming_ratings) - 1].copy()
    item['edf'] = float(1.0)
    edf_list.append(item)
    return {migration_matrix_struct['rating_scale_name']: {'edf': edf_list}}

def compute_rating_from_pd(idf,pd_ttc):
    if idf :
        lower_pd=None
        lower_rating=None
        upper_pd=None
        upper_rating=None
        for edf_obj in idf['edf']:
            current_pd=edf_obj['edf']
            if current_pd<=pd_ttc:
                lower_pd=current_pd
                lower_rating=edf_obj['rating_code']
            else:
                upper_pd=current_pd
                upper_rating=edf_obj['rating_code']
                break
        if lower_pd!=None:
            return (lower_rating,lower_pd,upper_rating,upper_pd)
        if upper_pd!=None:
            return (upper_rating,upper_pd, None, None)
    raise ValueError("Unknown rating from pd_ttc {} and idf : {}".format(pd_ttc,idf))