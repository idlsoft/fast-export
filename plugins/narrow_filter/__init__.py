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
        if filename == b'.hgignore':
            return b'.gitignore'
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

    def file_data_filter(self, file_data):
        if file_data['filename'] == b'.hgignore':
            data = file_data['data']
            lines = []
            for line in data.split(b'\n'):
                if line == b'syntax: glob' or line == '.git/':
                    continue
                if line.startswith(b'src/'):
                    line = b'**/' + line
                lparts = line.split(b'/')
                if len(lparts) > 1:
                    if lparts[-1] == b'*':
                        line = line[:-1]
                        if len(lparts) == 3 and lparts[0] == b'*':
                            line = line[2:]
                            lparts[0] = b''
                    if lparts[0] == b'*':
                        line = b'*' + line
                    if line.startswith(b'**/') and (len(lparts) == 2 or (len(lparts) == 3 and line.endswith(b'/'))):
                        line = line[3:]
                if line.startswith(b'rootglob:'):
                    line = b'/' + line[9:]
                if not line.startswith(b'*'):
                    lparts = line.split(b'/')
                    if len(lparts) > 2 or line.startswith(b'/'):
                        if line.startswith(b'/'):
                            line = line[1:]
                        if self.root:
                            if line.startswith(self.root):
                                line = b'/' + line[len(self.root):]
                            else:
                                continue
                        if self.prefixes:
                            for prefix in self.prefixes:
                                if line.startswith(prefix):
                                    line = b'/' + line
                                    break
                            else:
                                continue
                lines.append(line)
            file_data['data'] = b'\n'.join(lines)
