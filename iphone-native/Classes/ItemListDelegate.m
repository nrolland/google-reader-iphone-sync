#import "ItemListDelegate.h"
#import "ItemListController.h"
#import "ItemSet.h"
#import "TCHelpers.h"
#import "TagItem.h"

//@interface NSObject (MissingMethodTrace)
//@end
//
//@implementation NSObject (MissingMethodTrace)
//- (void) doesNotRecognizeSelector:(SEL)sel {
//	dbg(@"object %@ does not recognise selector: %s", self, sel);
//}
//@end

@implementation ItemListDelegate
- (id) init {
	return [self initWithTag:nil db:nil];
}

- (id) initWithTag:(NSString *) _tag db:(id)_db {
	self = [super init];
	tag = [_tag retain];
	db = [_db retain];
	return self;
}

- (id) tag {
	return tag;
}

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
	
	UIImage * image = nil;
	if([item hasChildren]) {
		image = [self folderImage];
	} else if([item is_starred]) {
		image = [self starredImage];
	}
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

- (UIImage *) folderImage {
	if(folderImage == nil) {
		folderImage = [UIImage imageNamed: @"emblem_folder.png"];
	}
	return folderImage;
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
	int itemIndex = [self itemIndexFromIndexPath:indexPath];
	id item = [[self itemSet] objectAtIndex: itemIndex];
	if([item hasChildren]) {
		dbg(@"pushing item onto nav: %@", item);
		ItemListController * newItemListController = [[[ItemListController alloc] init] autorelease];
		ItemListDelegate * newItemDelegate = [[[ItemListDelegate alloc] initWithTag: [item tagValue] db: db] autorelease];
		UITableView * newTableView = [[[UITableView alloc] init] autorelease];
		
		[newItemListController setDelegate: newItemDelegate];
		[newTableView setDelegate: newItemDelegate];
		[newTableView setDataSource: newItemDelegate];
		[newItemListController setView: newTableView];
		[newItemListController setListView: newTableView];
		// use the current "options" button for all views
		id rightButton = [[[navigationController navigationBar] topItem] rightBarButtonItem];
		[[newItemListController navigationItem] setRightBarButtonItem: rightButton];
		
		[navigationController pushViewController: newItemListController animated:YES];
	} else {
		// load it
		dbg(@"listdelegate: loading item: %@", item);
		[[[UIApplication sharedApplication] delegate] loadItemAtIndex: itemIndex fromSet: [self itemSet]];
	}
}

- (void) loadItemWithID:(NSString *) google_id {
	int index;
	id items = [self itemSet];
	id item;
	for(index == 0; index < [items count]; index++) {
		item = [items objectAtIndex:index];
		if([[item google_id] isEqualToString: google_id]) {
			[[[UIApplication sharedApplication] delegate] loadItemAtIndex: index fromSet: [self itemSet]];
			return;
		}
	}
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


- (void) reloadItems {
	[itemSet release];
	itemSet = nil;
}

- (void) setDB:(id) _db {
	[db release];
	db = [db retain];
	[self reloadItems];
}

- (id) itemSet {
	if(!itemSet) {
		itemSet = [[[ItemSet alloc] initWithTag: tag db: db] getItems];
		if(tag == nil) {
			// add the "All Items" tag
			itemSet = [NSMutableArray arrayWithArray: itemSet];
			[itemSet insertObject: [[[TagItem alloc] initWithTag: @"All Items" count: -1 db:db] autorelease] atIndex: 0];
		}
		[itemSet retain];
	}
	return itemSet;
}

- (void) setAllItemsReadState: (BOOL) readState {
	dbg(@"marking all items as read for tag: %@", tag);
	[db setAllItemsReadState: readState forTag: tag];
}

- (int)tableView:(id)view numberOfRowsInSection:(id)section {
	dbg(@"number of rows... %d", [[self itemSet] count]);
	return [[self itemSet] count];
}

- (void) dealloc {
	dbg(@"dealloc: %@", self);
	[starredImage release];
	[folderImage release];
	[readImage release];
	[readAndStarredImage release];
	[itemSet release];
	[cellFont release];
	[db release];
	[super dealloc];
}

@end
