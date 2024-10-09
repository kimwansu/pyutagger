


class BSP:
    def __init__(self, b, s, p):
        self.bsp = [b, s, p]
    
    @property
    def B(self):
        return self.bsp[0]
    
    @B.setter
    def B(self, b):
        self.bsp[0] = b
    
    @property
    def S(self):
        return self.bsp[1]
    
    @S.setter
    def S(self, s):
        self.bsp[1] = s
    
    @property
    def P(self):
        return self.bsp[2]
    
    @P.setter
    def P(self, p):
        self.bsp[2] = p
    
    @property
    def BS(self):
        b = self.bsp[0]
        s = self.bsp[1]
        if s:
            return f'{b}__{s}'
        else:
            return b
    
    @property
    def BP(self):
        b = self.bsp[0]
        p = self.bsp[2]
        return f'{b}/{p}'
    
    @property
    def BSP(self):
        b = self.bsp[0]
        s = self.bsp[1]
        p = self.bsp[2]
        if s:
            return f'{b}__{s}/{p}'
        else:
            return f'{b}/{p}'
            


def parse_sent(sent_str, flattern=False):
    bsps = []
    sent_str = sent_str.replace('+/SW', '/SW').replace('//SP', '/SP')
    ejs = sent_str.split(' ')
    tmp_ejs = []
    for ei, ej in enumerate(ejs):
        morphs = ej.split('+')
        for mi, morph in enumerate(morphs):
            if mi == len(morphs) - 1:
                end_ej = True
            else:
                end_ej = False
                
            if morph == '/SW':
                one_bsp = BSP('+', None, 'SW')
            elif morph == '/SP':
                one_bsp = BSP('/', None, 'SP')
            else:
                one_bsp = parse_bsp(morph)
                
            if flattern:
                bsps.append(one_bsp)
            else:
                tmp_ejs.append(one_bsp)
                if end_ej:
                    bsps.append(tmp_ejs)
                    tmp_ejs = []
            
    return bsps


def parse_bsp(bsp_str):
    body, pos = bsp_str.split('/')
    if '__' in bsp_str:
        body, sensenum = body.split('__')
    else:
        sensenum = None
    
    return [body, sensenum, pos]


