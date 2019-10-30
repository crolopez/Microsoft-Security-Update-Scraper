# Simple script to get the related patches to a given hotfix as an argument
#
# Use: python get_hotfix_deps.py <hotfix> <json format: yes/no>

from sys import argv
import requests as req
import re
import json


def get_patch_info(catalog_ids):
	patch_info = {'replaced_by': [], 'replaces': []}
	catalog_base = "https://www.catalog.update.microsoft.com/ScopedViewInline.aspx?updateid={0}"
	filter_repby_pattern = "<a href='ScopedViewInline.aspx?updateid="
	repby_patch_pattern = ">.*\((.*)\)<"
	reps_patch_pattern = "^[ ]+[^ <\n].*\((.*)\)"
	resp = req.get(catalog_base.format(catalog_ids[0]))
	replaced_by_section_str = "This update has been replaced by the following updates"
	replaces_section_str = "This update replaces the following updates"
	replaced_by_section = False
	replaces_section = False

	for line in resp.text.splitlines():
		if replaced_by_section_str in line: 
			replaced_by_section, replaces_section = True, False
		elif replaces_section_str in line: 
			replaced_by_section, replaces_section = False, True

		if replaced_by_section_str and filter_repby_pattern in line:
			patch = re.search(repby_patch_pattern, line)
			if patch and patch not in patch_info['replaced_by']:
				patch_info['replaced_by'].append(patch.group(1).replace('\n', ''))
		elif replaces_section:
			patch = re.search(reps_patch_pattern, line)
			if patch and patch not in patch_info['replaces']:
				patch_info['replaces'].append(patch.group(1).replace('\n', ''))

	return patch_info


def get_catalog_ids(kb):
	id_list = []
	catalog_base = "https://www.catalog.update.microsoft.com/Search.aspx?q={0}"
	filter_pattern = "onclick='goToDetails("
	kb_link_pattern = "onclick='goToDetails\(\"(.*)\"\)"
	resp = req.get(catalog_base.format(kb))

	for line in resp.text.splitlines():
		if filter_pattern in line:
			kb_link = re.search(kb_link_pattern, line)
			if kb_link:
				id_list.append(kb_link.group(1))

	return id_list


def main():
	patch = argv[1]
	json_format = True if argv[2] == "yes" else False
	catalog_ids = get_catalog_ids(patch)
	patch_info = get_patch_info(catalog_ids)

	if json_format:
		print(json.dumps(patch_info, indent=4, sort_keys=True))
		return

	print("****{0}****".format(patch))

	print("\nIncluded in:")
	for patch in patch_info['replaced_by']:
		print("{0}".format(patch))

	print("\nIncludes:")
	for patch in patch_info['replaces']:
		print("{0}".format(patch))


if __name__ == "__main__" :
    if len(argv) != 3:
      print("Use: python get_hotfix_deps.py <hotfix> <json format: yes/no>")
      exit(1)

    main()
