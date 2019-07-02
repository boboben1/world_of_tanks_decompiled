def dump(obj, fn):
    with open(fn, "w") as f:
        for attr in dir(obj):
            try:
                f.write("obj.%s = %r\n" % (attr, getattr(obj, attr)))
            except:
                pass
