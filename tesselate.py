def crop(Path,input,height,width,i,k,x,y,page):
    im = Image.open(input)
    imgwidth = im.size[0]
    imgheight = im.size[1]
    for i in range(0,imgheight-height/2,height-2):
        print i
        for j in range(0,imgwidth-width/2,width-2):
            print j
            box = (j, i, j+width, i+height)
            a = im.crop(box)
            a.save(os.path.join(Path,"PNG","%s" % page,"IMG-%s.png" % k))
            k +=1