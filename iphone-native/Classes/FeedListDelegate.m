#import "FeedListDelegate.h"
#import "tcHelpers.h"

@implementation FeedListDelegate

- tableView:(id)view cellForRowAtIndexPath: (id) indexPath {
	dbg(@"cellForRowAtPath: %@", indexPath);
	UITableViewCell * cell = [view dequeueReusableCellWithIdentifier:@"itemCell"];
	dbg(@"cell = %@", cell);
	if(cell == nil) {
		dbg(@"no cell - making one");
		cell = [[UITableViewCell alloc] initWithFrame: CGRectMake(0,0,1,1) reuseIdentifier:@"itemCell"];
		dbg(@"made one");
	}
	NSUInteger indexes[[indexPath length]];
	dbg(@"getting indexes");
	[indexPath getIndexes:indexes];
	dbg(@"indexes length = %u", [indexPath length]);
	[cell setText:[NSString stringWithFormat: @"cell %u", indexes[[indexPath length] - 1]]];
	dbg(@"returning %@", cell);
	return cell;
}

- (NSArray *)sectionIndexTitlesForTableView:(UITableView *)tableView {
	if(sectionNames == nil){
		sectionNames = [NSArray arrayWithObjects: @"Followed Feeds", @"Ignored Feeds", nil];
	}
	return sectionNames;
}

- (int) numberOfSectionsInTableView:(id)view {
	return 2;
}

- (int) tableView:(id)view numberOfRowsInSection:(id)section {
	return 8;
}

@end
