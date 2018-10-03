ctrys = dict();
>>> for city in d[u'features']:
...     n = city[u'properties'][u'ADM0NAME']
...     if n in ctrys:
...             ctrys[n] = ctrys[n] + 1
...     else:
...             ctrys[n] = 1



#process out the features in the countries, other than name (from geojson)

def centroid(geom):
	if geom[u'geometry'][u'type']==u'Polygon':
		coords = [i for x in geom[u'geometry'][u'coordinates'] for i in x]
	elif geom[u'geometry'][u'type']==u'MultiPolygon':
		coords = [j for x in geom[u'geometry'][u'coordinates'] for i in x for j in i]
	l = len(coords)
	total = reduce(lambda a,b: [a[0]+b[0],a[1]+b[1]], coords)
	return [total[0]/l,total[1]/l]

smallfeatures = []
for feat in ctry[u'features']:
	smallfeatures.append({})
	smallfeatures[-1][u'geometry'] = feat[u'geometry']
	smallfeatures[-1][u'type'] = feat[u'type']
	center = centroid(feat)
	smallfeatures[-1][u'properties'] = {u'name':feat[u'properties'][u'name'], u'centre':center}
smallctry = {u'type':ctry[u'type'],u'bbox':ctry[u'bbox'],u'features':smallfeatures}
json.dump(
