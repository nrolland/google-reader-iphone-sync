#import "ItemListDelegate.h"
#import "tcHelpers.h"

@implementation ItemListDelegate

- tableView:(id)view cellForRowAtIndexPath: (id) indexPath {
	UITableViewCell * cell = [view dequeueReusableCellWithIdentifier:@"itemCell"];
	if(cell == nil) {
		cell = [[UITableViewCell alloc] initWithFrame: CGRectMake(0,0,1,1) reuseIdentifier:@"itemCell"];
	}
	
	id item = [self itemAtIndexPath:indexPath];
	[cell setText: [item title]];
	
	UIColor * textColor = [item is_read] ? [UIColor lightGrayColor] : [UIColor blackColor]; // nil should work (for black), but doesn't
	[cell setTextColor: textColor];
	
	UIImage * image;
	if([item userHasMarkedAsUnread]) {
		image = [item is_starred] ? [self readAndStarredImage] : [self readImage];
	} else {
		image = [item is_starred] ? [self starredImage] : nil;
	}
	[cell setImage: image];
	
	return cell;
}

- (UIImage *) starredImage {
	if(starredImage == nil) {
		starredImage = [UIImage imageNamed: @"emblem_starred.png"];
	}
	return starredImage;
}

- (UIImage *) readImage {
	if(readImage == nil) {
		readImage = [UIImage imageNamed: @"emblem_read.png"];
	}
	return readImage;
}

- (UIImage *) readAndStarredImage {
	if(readAndStarredImage == nil) {
		readAndStarredImage = [UIImage imageNamed: @"emblem_read_and_starred.png"];
	}
	return readAndStarredImage;
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

- (id) getIndexPathForItemWithID:(NSString *) google_id {
	int foundAtIndex = 0;
	int index;
	
	itemSet = [self itemSet];
	int count = [itemSet count];
	for(index = 0; index < count; index++) {
		if([[[itemSet objectAtIndex:index] google_id] isEqualToString: google_id]) {
			// found it!
			dbg(@"found item with id %@ at index %d", google_id, index);
			foundAtIndex = index;
			break;
		}
	}
	NSUInteger indexes[2];
	indexes[0] = 0;
	indexes[1] = foundAtIndex;
	return [NSIndexPath indexPathWithIndexes:indexes length:2];
}

- (void) setItemSet:(id)newItemSet {
	[itemSet release];
	itemSet = [newItemSet retain];
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
	[starredImage release];
	[readImage release];
	[readAndStarredImage release];
	[itemSet release];
	[super dealloc];
}

@end
