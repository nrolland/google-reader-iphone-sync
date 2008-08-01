#import "ItemListDelegate.h"
#import "tcHelpers.h"

@implementation ItemListDelegate

- tableView:(id)view cellForRowAtIndexPath: (id) indexPath {
	dbg(@"cellForRowAtPath: %@", indexPath);
	UITableViewCell * cell = [view dequeueReusableCellWithIdentifier:@"itemCell"];
	dbg(@"cell = %@", cell);
	if(cell == nil) {
		dbg(@"no cell - making one");
		cell = [[UITableViewCell alloc] initWithFrame: CGRectMake(0,0,1,1) reuseIdentifier:@"itemCell"];
		dbg(@"made one");
	}
	
	[cell setText: [[self itemAtIndexPath:indexPath] title]];
	dbg(@"returning %@", cell);
	return cell;
}

- (int)numberOfSectionsInTableView:(id)view {
	return 1;
}

- (id) itemAtIndexPath: (id) indexPath {
	id item = [[self itemSet] objectAtIndex: [self itemIndexFromIndexPath: indexPath]];
	dbg(@"item = %@", item);
	return item;
}

- (NSUInteger) itemIndexFromIndexPath: (id) indexPath {
	dbg(@"index path %@ length is %u", indexPath, [indexPath length]);
	NSUInteger index = [indexPath indexAtPosition: [indexPath length] - 1];
	dbg(@"returned index is %u", index);
	return index;
}

- (void) tableView:(id)view didSelectRowAtIndexPath:(id) indexPath {
	[[[UIApplication sharedApplication] delegate] loadItemAtIndex: [self itemIndexFromIndexPath:indexPath] fromSet: itemSet];
}

- (void) deleteItemCache {
	[itemSet release];
	itemSet = nil;
}

- (id) itemSet {
	// ensure it exists
	if(itemSet == nil) {
		dbg(@"allocating itemSet");
		itemSet = [[[db allItems] allObjects] retain];
		dbg(@"itemset is %@", itemSet);
	}
	return itemSet;
}

- (int)tableView:(id)view numberOfRowsInSection:(id)section {
	dbg(@"how many items? %d!!", [[self itemSet] count]);
	return [[self itemSet] count];
}

- (void) dealloc {
	[itemSet release];
	[super dealloc];
}

@end
