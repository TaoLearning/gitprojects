import argparse
import github
import sys
import csv

from github import Github


def main():
	parser = argparse.ArgumentParser(description='Create a table depicting of up to 5 milestones with the status of each issue inside them.')
	parser.add_argument('token', type=str, help='Your GitHub (public or enterprise) personal access token')
	parser.add_argument('repo', type=str, help='the team and repo to migrate from: <team_name>/<repo_name>')
	parser.add_argument('--root', '-sr', nargs='?', default='https://api.github.com', type=str, help='The GitHub domain to migrate from. Defaults to https://www.github.com. For GitHub enterprise customers, enter the domain for your GitHub installation.')
	args = parser.parse_args()

	repo = args.repo
	github_wth_token = Github(args.token)

	if (args.root != 'https://api.github.com'):
		args.root += '/api/v3'

	source = github_wth_token.get_repo(repo)

	###### MILESTONES #######
	all_milestones = source.get_milestones()
	if all_milestones:
		out = csv.writer(open("milestones_" + repo.split("/")[1] + ".csv","w"), delimiter=',',quoting=csv.QUOTE_ALL)
		gh_exception = github.GithubException
		for milestone in all_milestones:
			try:
				out.writerow([milestone.id, milestone.title, milestone.due_on])
				print("Created Milestone: "+milestone.title)
			except gh_exception as e:
				if e.status == 422:
					if args.update == True:
						print("Ability to update Milestone "+milestone.title+" coming in next version. Skipping.")
					else:
						print("Milestone "+milestone.title+" already exists. Skipping.")
			except AssertionError:
				print("Skipping Milestone: "+milestone.title+". Add manually if needed.")
	elif all_milestones == False:
		print("ERROR: Milestones failed to be retrieved. Exiting...")
		sys.exit(1)
	else:
		print("No milestones found. None migrated")

	###### ISSUES #######
	all_issues = source.get_issues()
	if all_issues:
		out = csv.writer(open("issues_" + repo.split("/")[1] + ".csv","w"), delimiter=',',quoting=csv.QUOTE_ALL)
		gh_exception = github.GithubException
		for issue in all_issues:
			try:
				print("Created Issue: "+issue.title)
				out.writerow([issue.number, issue.title])
			except gh_exception as e:
				if e.status == 422:
					print("Issue "+issue.title+" already exists. Skipping.")
			except AssertionError:
				print("Skipping Issue: "+issue.title+". Add manually if needed.")
	elif all_issues == False:
		print("ERROR: Issues failed to be retrieved. Exiting...")
		sys.exit(1)
	else:
		print("No issues found. None migrated")

	sys.exit(0)


# 🔨 <a href="https://github.com/TaoFruit/iguanahive/milestone/1">LifeCycle Mgt</a> 	| 👯 Customer Journey 	| 📑 Narratives 	|
# |-	|-	|-	|
# | :white_check_mark: Dream 	| :black_square_button: UX Research 	|  :black_square_button: ReadMe 	|
# | :white_check_mark: Discovery 	| :black_square_button: UI Design 	| :black_square_button: Documentation 	|
# | :white_check_mark: Development 	| :black_square_button: Brand Identity 	| :black_square_button: Business Plan 	|
# | :black_square_button: Deployment 	| :black_square_button: Call to Actions 	| :black_square_button: Proposal 	|
# | :black_square_button: Discipline 	| :black_square_button: Copywriting 	| :black_square_button: Technical Documenation 	|
# | :black_square_button: Disposal 	| :black_square_button: Sales Funnel	| :black_square_button: Stats &amp; Results 	|

if __name__ == "__main__":
	main()