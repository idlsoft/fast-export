def build_filter(args):
    s = args.encode().split(b':')
    if len(s) == 1:
        root = None
        prefixes = s[0].split(b',')
    elif len(s) == 2:
        root = s[0]
        prefixes = s[1].split(b',') if s[1] else None
    else:
        raise ValueError(f'Unsupported args for {__name__}: {args}')
    from mercurial import localrepo
    localrepo.localrepository._basesupported.add(b'narrowhg-experimental')
    return Filter(root, prefixes)

class Filter:
    def __init__(self, root, prefixes):
        self.root = root
        self.prefixes = prefixes

    def file_name_filter(self, filename):
        if b'/out/production/' in filename or b'/out/test/' in filename:
            return ''
        if self.root:
            if not filename.startswith(self.root):
                return ''
            filename = filename[len(self.root):]
        if self.prefixes:
            for prefix in self.prefixes:
                if filename.startswith(prefix):
                    return filename
            filename = ''
        return filename
