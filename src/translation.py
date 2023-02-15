import csv

class Translation:
	def __init__(self, language):
		self._language = language
		self._table = {}
		with open('language.csv', "r") as f:
			reader = csv.reader(f)
			header = next(reader)
			languages = header[1:]
			for l in languages:
				self._table[l] = {}
			for row in reader:
				for k in range(len(languages)):
					l = languages[k]
					self._table[l][row[0]] = row[k+1]
	
	def __getattr__(self, resource_id):
		if not self._language in self._table:
			raise ValueError(f"No translations found for language {self._language}")
		if not resource_id in self._table[self._language]:
			raise ValueError(f"No translation found for resource ID {resource_id} in language {self._language}")
		return self._table[self._language][resource_id]