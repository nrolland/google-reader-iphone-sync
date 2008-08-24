#import "ItemListDelegate.h"
#import "tcHelpers.h"

@implementation ItemListDelegate
- (id) tableView:(id)view cellForRowAtIndexPath: (id) indexPath {
	UITableViewCell * cell = [view dequeueReusableCellWithIdentifier:@"itemCell"];
	if(cell == nil) {
		cell = [[UITableViewCell alloc] initWithFrame: CGRectMake(0,0,1,1) reuseIdentifier:@"itemCell"];
		[cell setFont: [self cellFont]];
		[cell setLineBreakMode: UILineBreakModeWordWrap];
	}
	
	id item = [self itemAtIndexPath:indexPath];
	[cell setText: [item title]];
	
	UIColor * textColor = [item is_read] ? [UIColor lightGrayColor] : [UIColor blackColor]; // nil should work (for black), but doesn't
	[cell setTextColor: textColor];
	
	UIImage * image;
	image = [item is_starred] ? [self starredImage] : nil;
	// if([item userHasMarkedAsUnread]) {
	// 	image = [item is_starred] ? [self readAndStarredImage] : [self readImage];
	// } else {
	// 	image = [item is_starred] ? [self starredImage] : nil;
	// }
	[cell setImage: image];
	
	UITableViewCellSelectionStyle selStyle = [item is_read]? UITableViewCellSelectionStyleGray : UITableViewCellSelectionStyleBlue;
	[cell setSelectionStyle: selStyle];
	
	return cell;
}


- (UIFont *) cellFont {
	if(cellFont == nil) {
		cellFont = [[UIFont systemFontOfSize:16.0] retain];
	}
	return cellFont;
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
	return item;
}

- (NSUInteger) itemIndexFromIndexPath: (id) indexPath {
	NSUInteger index = [indexPath indexAtPosition: [indexPath length] - 1];
	return index;
}

- (void) tableView:(id)view didSelectRowAtIndexPath:(id) indexPath {
	[[[UIApplication sharedApplication] delegate] loadItemAtIndex: [self itemIndexFromIndexPath:indexPath] fromSet: itemSet];
}

- (void) loadItemWithID:(NSString *) google_id {
	int index;
	id items = [self itemSet];
	id item;
	for(index == 0; index < [items count]; index++) {
		item = [items objectAtIndex:index];
		if([[item google_id] isEqualToString: google_id]) {
			[[[UIApplication sharedApplication] delegate] loadItemAtIndex: index fromSet: itemSet];
			return;
		}
	}
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

- (void) setAllItemsReadState: (BOOL) readState {
	[db setAllItemsReadState: readState];
}

- (id) itemSet {
	// ensure it exists
	if(itemSet == nil) {
		[self setItemSet: [self getNewItemSet]];
	}
	return itemSet;
}

- (id) getNewItemSet {
	id itemSet;
	if([settings showReadItems]) {
		itemSet = [[db allItems] allObjects];
	} else {
		itemSet = [[db unreadItems] allObjects];
	}
	return itemSet;
}

- (void) reloadItems {
	[self setItemSet: [self getNewItemSet]];
	dbg(@"reloading data...");
	[listView reloadData];
	// TODO: why is this not working?
	[listView setNeedsDisplay]; // this shouldn't be necessary, surely...
}

- (int)tableView:(id)view numberOfRowsInSection:(id)section {
	return [[self itemSet] count];
}

- (void) dealloc {
	[starredImage release];
	[readImage release];
	[readAndStarredImage release];
	[itemSet release];
	[cellFont release];
	[super dealloc];
}

@end
