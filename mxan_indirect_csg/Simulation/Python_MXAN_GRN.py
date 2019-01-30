class InternalNetwork:
    def __init__(self, state):
        self.state = state
        rules = {}
        rules['NUT']    = "self.state['NUT']"
        rules['RELA']   = "not self.state['NUT']"
        rules['ASGAB']  = "self.state['RELA']"
        rules['ASGE']   = "not self.state['NUT'] and self.state['NLA6']"
        rules['ASG']    = "self.state['ASG']"
        rules['NLA4']   = "self.state['RELA']"
        rules['NLA18']  = "self.state['RELA']"
        rules['NLA6']   = "not self.state['MAZF'] and (self.state['NLA4'] & self.state['NLA18'])"
        rules['NLA28']  = "self.state['NLA6'] and self.state['ASG']"
        rules['CSGA']   = "self.state['CSGA']"
        rules['PKTD9']  = "self.state['NUT']"
        rules['PEP']    = "self.state['NUT']"
        rules['PKTD1']  = "self.state['PEP']"
        rules['MKAPB']  = "self.state['PKTD1']"
        rules['PKTA4']  = "self.state['MKAPB']"
        rules['MKAPA']  = "self.state['PKTD9'] or self.state['PKTA2'] or self.state['PKTA4']"
        rules['PKTA2']  = "self.state['DEVTRS']"
        rules['PKTC2']  = "self.state['MKAPA']"
        rules['PSKA5']  = "self.state['PKTC2']"
        rules['MRPC2']  = "self.state['ASG'] and not self.state['PSKA5'] and not self.state['MAZF']"
        rules['FRUA']   = "self.state['FRUA']"
        rules['DEVTRS'] = "self.state['MRPC2'] or self.state['FRUA']"
        rules['MAZF']   = "not self.state['NUT'] and not self.state['DEVTRS'] and (self.state['MAZF'] or self.state['MRPC2'])"
        self.rules = rules
        self.synchrony = 0
    def update(self):
        state_prime = self.state.copy()
        for node in self.state:
            if self.synchrony == 0:
                if node != "MAZF":
                    state_prime[node] = eval(self.rules[node])
            else:
                state_prime[node] = eval(self.rules[node])
		self.state = state_prime.copy()
        self.synchrony = 1 - self.synchrony
    def mutate(self, node, value):
		self.rules[node] = value
    def numeric_state(self):
		state = 0
		pos   = 0
		nodes = self.state.keys()
		nodes.sort()
		for node in nodes:
			state += int(self.state[node])*2**pos
			pos += 1
		return(state)
    
    
    
    
#state = {'NUT': False, 'RELA': True, 
#    'ASGAB': True, 'ASGE': False, 'ASG': True,
#    'NLA4': True, 'NLA18': True, 'NLA6': True, 'NLA28': False, 'CSGA': False,
#    'PKTD9': True, 'PEP': True, 'PKTD1': False, 'MKAPB': False, 'PKTA4': False,
#    'PKTA2': False, 'MKAPA': True, 'PKTC2': True, 'PSKA5': True,
#    'MRPC2': False, 'FRUA': True, 'DEVTRS': False, 'MAZF': False}

#x = GRN(state)

#x.numeric_state()
#x.update()
#x.state['DEVTRS'], x.state['MAZF'], x.state['MRPC2'], x.state['NLA6']