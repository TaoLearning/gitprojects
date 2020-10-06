import argparse
import github
import sys

from github import Github


def main():
	parser = argparse.ArgumentParser(description='Migrate Milestones, Labels, and Issues between two GitHub repositories. To migrate a subset of elements (Milestones, Labels, Issues), use the element specific flags (--milestones, --lables, --issues). Providing no flags defaults to all element types being migrated.')
	parser.add_argument('user_name', type=str, help='Your GitHub (public or enterprise) username: name@email.com')
	parser.add_argument('token', type=str, help='Your GitHub (public or enterprise) personal access token')
	parser.add_argument('source_repo', type=str, help='the team and repo to migrate from: <team_name>/<repo_name>')
	parser.add_argument('destination_repo', type=str, help='the team and repo to migrate to: <team_name>/<repo_name>')
	parser.add_argument('--destinationToken', '-dt', nargs='?', type=str, help='Your personal access token for the destination account, if you are migrating between GitHub installations')
	parser.add_argument('--destinationUserName', '-dun', nargs='?', type=str, help='Username for destination account, if you are migrating between GitHub installations')
	parser.add_argument('--sourceRoot', '-sr', nargs='?', default='https://api.github.com', type=str, help='The GitHub domain to migrate from. Defaults to https://www.github.com. For GitHub enterprise customers, enter the domain for your GitHub installation.')
	parser.add_argument('--destinationRoot', '-dr', nargs='?', default='https://api.github.com', type=str, help='The GitHub domain to migrate to. Defaults to https://www.github.com. For GitHub enterprise customers, enter the domain for your GitHub installation.')
	parser.add_argument('--milestones', '-m', action="store_true", help='Toggle on Milestone migration.')
	parser.add_argument('--labels', '-l', action="store_true", help='Toggle on Label migration.')
	parser.add_argument('--issues', '-i', action="store_true", help='Toggle on Issue migration.')
	parser.add_argument('--update', '-u', action="store_true", help='Toggle on Update Existing.')
	args = parser.parse_args()

	destination_repo = args.destination_repo
	source_repo = args.source_repo
	github_with_token = Github(args.token)

	if (args.sourceRoot != 'https://api.github.com'):
		args.sourceRoot += '/api/v3'

	if (args.destinationRoot != 'https://api.github.com'):
		args.destinationRoot += '/api/v3'

	if (args.sourceRoot != args.destinationRoot):
		if not (args.destinationToken):
			print("Error: Source and Destination Roots are different but no token was supplied for the destination repo.")
			sys.exit(1)

	if not (args.destinationUserName):
		print('No destination User Name provided, defaulting to source User Name: '+args.user_name)
		args.destinationUserName = args.user_name

	destination_credentials = Github(args.destinationToken)   
    
	source_root = args.sourceRoot+'/'
	destination_root = args.destinationRoot+'/'

	milestone_map = None

	if args.milestones == False and args.labels == False and args.issues == False:
		args.milestones = True
		args.labels = True
		args.issues = True

	source = github_with_token.get_repo(source_repo)
	destination = github_with_token.get_repo(destination_repo)

	###### MILESTONES #######
	if args.milestones:
		all_milestones = source.get_milestones()
		if all_milestones:
			create_milestone = destination.create_milestone
			gh_exception = github.GithubException
			for milestone in all_milestones:
				try:
					var = create_milestone(title=milestone.title, state=milestone.state, description=milestone.description, due_on=milestone.due_on)
					print("Created Milestone: "+milestone.title)
				except gh_exception as e:
					if e.status == 422:
						if args.update == True:
							# TASK: Add ability to update existing milestones. ###############################
							# destination.get_milestone(existing.number).edit(title=milestone.title, state=milestone.state, description=milestone.description)
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
	
	###### LABELS #######
	if args.labels:
		all_labels = source.get_labels()
		if all_labels:
			create_label = destination.create_label
			gh_exception = github.GithubException
			for label in all_labels:
				try:
					create_label(name=label.name, color=label.color, description=label.description)
					print("Created Label: "+label.name)
				except gh_exception as e:
					if e.status == 422:
						print("Label "+label.name+" already exists. Skipping.")
		elif all_labels == False:
			print("ERROR: Labels failed to be retrieved. Exiting...")
			sys.exit(1)
		else:
			print("No labels found. None migrated")

	###### ISSUES #######
	if args.issues:
		all_issues = source.get_issues()
		if all_issues:
			for issue in all_issues:
				try:
					destination.create_issue(title=issue.title, body=issue.body, assignees=issue.assignees, milestone=issue.milestone, labels=issue.labels)
					print("Created Issue: "+issue.title)
				except github.GithubException as e:
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

if __name__ == "__main__":
	main()