def generateSvg(filename, log, width=-1, height=-1, strokeWidth=2):
    #formats log to msgs[id] -> [msg, source, t0, t1]
    msgs = {}
    times = []
    nodes = []
    for time, msg, source in log:
        if source is not None:
            source = source.name
        #save all time and nodes for sizing
        times += [time]
        if msg.dstNode not in nodes:
            nodes += [msg.dstNode]
        if source is not None and source not in nodes:
            nodes += [source]
            
        id = msg._id
        #sender/external event
        if id not in msgs:
            msgs[id] = [msg, source, time]
        #receiver
        else:
            msgs[id] += [time]
            
    startTime = min(times)
    endTime = max(times)
    
    timeSpacing = 2.0
    #default
    if width == -1:
        width = (endTime-startTime+timeSpacing)*6
    #modifier (e.g. '10x')
    elif isinstance(width, str):
        width = (endTime-startTime+timeSpacing)*6 * float(width.split('x')[0])
    #default
    if height == -1:
        height = (len(nodes)+1.0)*10 
    #modifier
    elif isinstance(height, str):
        height = (len(nodes)+1.0)*10  * float(height.split('x')[0])
    hSpacing = width/(endTime-startTime+(2*timeSpacing))
    vSpacing = height/(len(nodes)+1.0)
    
    nodeHeight = {}
    count = 0
    for n in nodes:
        count += 1
        nodeHeight[n] = vSpacing*count
        
    svg = open(filename, 'w')
    svg.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE svg>\n')
    svg.write('<svg width="{}" height="{}" xmlns="http://www.w3.org/2000/svg">\n'.format(width, height))
    svg.write('\t<rect fill="#fff" stroke="#000" x="0" y="0" width="{}" height="{}"/>\n'.format(width, height))
    
    #node lines
    for n in nodes:
        svg.write('\t<text y="{}" x="{}">{}</text>\n'.format(nodeHeight[n], vSpacing*0.5, n))
        svg.write('\t<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="black" stroke-width="{}" />\n'.format(hSpacing*2, nodeHeight[n], width-vSpacing, nodeHeight[n], strokeWidth))
        
    #diagonal lines 
    svg.write('\n')
    arrowModifier = 5.0
    diagSize = ((vSpacing**2) + (hSpacing**2)) ** 0.5
    for id in msgs:
        source = msgs[id][1]
        #message between nodes
        if source is not None:
            msg, source, t0, t1 = msgs[id]
            fromH = nodeHeight[source]
            toH = nodeHeight[msg.dstNode]
            #svg.write('<g fill="none" stroke="black" stroke-width="{}">'.format(strokeWidth/2)))
            svg.write('\t<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="black" stroke-width="{}" />\n'.format((t0+timeSpacing)*hSpacing, fromH, (timeSpacing+t1)*hSpacing, toH, strokeWidth/2))
            #make an arrow at dst
            #toH under
            if fromH < toH:
                svg.write('\t <line x1="{}" y1="{}" x2="{}" y2="{}" stroke="black" stroke-width="{}" />\n'.format((timeSpacing+t1-(0.2))*hSpacing, toH-(vSpacing/arrowModifier), (timeSpacing+t1)*hSpacing, toH, strokeWidth/2))
                svg.write('\t <line x1="{}" y1="{}" x2="{}" y2="{}" stroke="black" stroke-width="{}" />\n'.format((timeSpacing+t1-(0.8))*hSpacing, toH-(vSpacing/(arrowModifier*5)), (timeSpacing+t1)*hSpacing, toH, strokeWidth/2))
            #toH above
            elif toH < fromH:
                svg.write('\t <line x1="{}" y1="{}" x2="{}" y2="{}" stroke="black" stroke-width="{}" />\n'.format((timeSpacing+t1-(0.2))*hSpacing, toH+(vSpacing/arrowModifier), (timeSpacing+t1)*hSpacing, toH, strokeWidth/2))
                svg.write('\t <line x1="{}" y1="{}" x2="{}" y2="{}" stroke="black" stroke-width="{}" />\n'.format((timeSpacing+t1-(0.8))*hSpacing, toH+(vSpacing/(arrowModifier*5)), (timeSpacing+t1)*hSpacing, toH, strokeWidth/2))
            
    svg.write('\n')
    #diagonal text
    for id in msgs:
        source = msgs[id][1]
        #message between nodes
        if source is not None and msg.text is not None:
            msg, source, t0, t1 = msgs[id]
            fromH = nodeHeight[source]
            toH = nodeHeight[msg.dstNode]
            svg.write('\t<text y="{}" x="{}" stroke="red">{}</text>\n'.format((fromH+toH)/2, (timeSpacing+t0+((t1-t0)/2.0))*hSpacing, msg.text))
                
    
    svg.write('</svg>')
    svg.close()