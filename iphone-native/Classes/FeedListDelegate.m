#import "FeedListDelegate.h"
#import "tcHelpers.h"

@implementation FeedListDelegate
- (void) dealloc {
	[selectedFeedList release];
	[feedList release];
}

- (void) setSelectedFeeds: feeds {
	[selectedFeedList retain];
	selectedFeedList = [[NSMutableArray alloc] initWithArray: feeds];
}

- (void) setFeedList: feeds {
	[feedList release];
	feedList = [[NSMutableArray alloc] initWithArray: feeds];;
}

- tableView:(id)view cellForRowAtIndexPath: (id) indexPath {
	UITableViewCell * cell = [view dequeueReusableCellWithIdentifier:@"feedListCell"];
	if(cell == nil) {
		cell = [[UITableViewCell alloc] initWithFrame: CGRectMake(0,0,1,1) reuseIdentifier:@"feedListCell"];
		[cell setSelectionStyle: UITableViewCellSelectionStyleNone];
	}
	NSUInteger indexes[[indexPath length]];
	[indexPath getIndexes:indexes];
	if(feedList) {
		NSString * feedName = [feedList objectAtIndex: [tcHelpers lastIndexInPath:indexPath]];
		[cell setText:feedName];
		UIColor * textColor;
		if([selectedFeedList containsObject: feedName]) {
			[cell setAccessoryType: UITableViewCellAccessoryCheckmark];
			textColor = [UIColor blackColor];
		} else {
			[cell setAccessoryType: UITableViewCellAccessoryNone];
			textColor = [UIColor lightGrayColor];
		}
		
		[cell setTextColor: textColor];
	} else {
		[cell setText:@"Unable to get feed list"];
		[cell setAccessoryType: UITableViewCellAccessoryNone];
	}
	return cell;
}

- (int) numberOfSectionsInTableView:(id)view {
	return 1;
}

- (void) tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
	if(feedList) {
		NSString * selectedFeed = [feedList objectAtIndex: [tcHelpers lastIndexInPath:indexPath]];
		if([selectedFeedList containsObject:selectedFeed]) {
			[selectedFeedList removeObject:selectedFeed];
		} else {
			[selectedFeedList addObject: selectedFeed];
		}
	}
	[tableView reloadData];
	[appSettings setTagList: selectedFeedList];
}

- (int) tableView:(id)view numberOfRowsInSection:(id)section {
	if(!feedList) {
		return 1;
	} else {
		return [feedList count];
	}
}

@end
