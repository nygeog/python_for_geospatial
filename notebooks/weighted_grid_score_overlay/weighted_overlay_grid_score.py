def weighted_grid_score_overlay(data):
    layer_list = []  # list for layers to sum at end for sum_weight
    
    for k in data.keys():
        data[k]['geodataframe'] = gpd.read_file(f'data/input/{k}.shp')         
         
        if data[k]['type'] == 'study_grid':
            grid = data[k]['geodataframe']
            grid['uid'] = grid.index + 1

    for k in data.keys():
        if data[k]['type'] == 'point':  # buffer point layers
            gdf = data[k]["geodataframe"]
            gdf['geometry'] = gdf.buffer(data[k]["buffer_dist"])
            data[k]['geodataframe'] = gdf
            gdf.to_file(f'data/processing/buffer_{k.lower()}.shp')

        if data[k]['type'] != 'study_grid':  # for all layers not the grid
            layer = data[k]['geodataframe']
            k_name = k.lower()  # lowercase layer name
            layer_list.append(k_name)
        
            intersect = gpd.overlay(grid, layer, how='intersection')
            intersect[f'{k_name}_area_sqkm'] = intersect.geometry.area  # calculate area
            intersect[f'{k_name}_weighted_area'] = intersect[f'{k_name}_area_sqkm'] * data[k]["weight"] 

            intersect.to_file(f'data/processing/grid_int_{k.lower()}.shp')

            df = intersect[
                ['uid', f'{k_name}_area_sqkm', f'{k_name}_weighted_area']
            ].groupby(
                ['uid'],
                as_index=False,
            ).sum()  # create summary weights dataframe
            
            data[k]['summary_weights'] = df  
            grid = grid.merge(
                df[['uid', f'{k_name}_weighted_area']],
                on='uid', 
                how='left',
            )
        
    grid['sum_weight'] = grid[[f'{i}_weighted_area' for i in layer_list]].sum(axis=1)
        
    return grid, data