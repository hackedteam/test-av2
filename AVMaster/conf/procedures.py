import yaml
import pprint as pp

f = open("procedures.yaml")
y = yaml.load(f)

pp.pprint(y)