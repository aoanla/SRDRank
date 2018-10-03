import networkx
import numpy as np
#confidences code for subgroup detection, now in a function
def confidences(sg):
        #capacity for an edge is the same as effective stiffness
        def calc_capacity(kfactor):
                return np.exp(-kfactor);


        #we don't do this for anything but the dominant group
        for e in sg.edges(data='kfactor'): #iterate through the edges, adding their capacity property so minimum_cut can work
                #fix due to changes in edges selector functionality in newer versions of networkx....
                sg[e[0]][e[1]]['capacity'] = calc_capacity(e[2]); #change back, I think this works? selector should definitely mean that the "value" of elements of e is "kfactor" value


        def node_cap(G,node): #the Capacity of the node, formally (the sum of all links from the node)
                return sum([e['capacity'] for e in G[node].values()])
	
	def node_max(G, node): #the Maximum link of the node - the strongest link directly connected to the node (a measure of recency only)
		return max([e['capacity'] for e in G[node].values()])

        subnames = sg.nodes()

        maxnode = sorted(subnames, key=lambda l:node_cap(sg,l))[-1]
        #maxnode_m = sorted(men_teams, key=lambda l:node_cap(subgraphs[0],l))[-1]

        #get minimum cuts for routes to the most connected node, maxnode [except for maxnode, which obviously can't be tested against itself]
        globalparts = {n:networkx.minimum_cut(sg,maxnode,n) for n in subnames if n != maxnode}

        connectivity = {n:{'global':globalparts[n][0], 'pivot':False, 'local':globalparts[n][0], 'localpart':0, 'maxlink':node_max(sg,n) } for n in subnames if n != maxnode }

        connectivity[maxnode] = {'global':node_cap(sg,maxnode),'pivot': True, 'local':node_cap(sg,maxnode),'localpart':0, 'maxlink':node_max(sg,maxnode) }

        #global connectivity is globalparts[n][0] for all nodes but maxnode (which has connectivity = node_cap(subgraphs[0],maxnode) by definition)

        #now, find our valid subgroups: - we (arbitrarily) decide that sensible subgroups must be at least 11 teams in size... and (formally) that a subgroup must be < half the size of the total group!
        potential_subparts = sorted([[x[1][1],False] for x in globalparts.values() if len(x[1][1]) > 10 and len(x[1][1]) < len(globalparts)/2 ],key=lambda s:-len(s[0]))
        #now we need to winnow these down to eliminate smaller groups which are subsets of the larger (we only want 1 level of subset partitioning here!)
        for n in range(len(potential_subparts)):    #operate on sorted copy of list, as we want to go from largest subsets first
                if potential_subparts[n][1] == True:
                        continue #already marked as a subset
                for l in potential_subparts[n+1:]: #else check all remaining subparts to see if we own them
                        if l[1] == True:
                                continue #already someone else's subset
                        l[1] = potential_subparts[n][0].issuperset(l[0])

        #the true subparts are those which are not subsets of larger subparts
        true_subparts = [x[0] for x in potential_subparts if x[1] is False]

        for i in range(len(true_subparts)):
                partset = list(true_subparts[i])
                local_maxnode = sorted(partset, key=lambda l:node_cap(sg,l))[-1]
                connectivity[local_maxnode]['local'] = node_cap(sg,local_maxnode)
                connectivity[local_maxnode]['localpart'] = i+1
                connectivity[local_maxnode]['pivot'] = True
                for p in [x for x in partset if x != local_maxnode]:
                        connectivity[p]['localpart'] = i+1
                        connectivity[p]['local'] = networkx.minimum_cut(sg,local_maxnode,p)[0]
                #connectivity is keyed by id
                #  - values are 'global' - a global confidence measure, 
                #               'localpart' - a local subgroup id
                #                                       'local' - the (intra)subgroup confidence measure
                #                'pivot' - "is this the pivot of the subgroup?"
        return connectivity

