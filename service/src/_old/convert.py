import sys
import yaml
import json

stream = open("template.yaml", "r")
docs = yaml.load_all(stream)

print(docs)


# for doc in docs:
#     for k,v in doc.items():
#         print(k, "->", v)
#     print("\n",)

# print(yamll)
# json.dump(yamll, "template.json", indent=4)