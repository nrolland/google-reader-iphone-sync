# cheerfully stolen from http://snippets.dzone.com/posts/show/5116
class OpenStruct:
	def __init__(self, **dic):
		self.__dict__.update(dic)
	def __getattr__(self, i):
		if i in self.__dict__:
			return self.__dict__[i]
		else:
			raise AttributeError, i
	def __setattr__(self,i,v):
		if i in self.__dict__:
			self.__dict__[i] = v
		else:
			self.__dict__.update({i:v})
		return v
