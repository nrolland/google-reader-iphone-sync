#import "ItemView.h"
#import "ItemDirList.h"
#import "TCHelpers.h"

@implementation ItemView
- (void) awakeFromNib {
	[self blacken];
	[super awakeFromNib];
}

- (void) load {
	[self allItems];
	if(currentItem == nil) {
		[self loadItemAtIndex:0];
	}
}

- (id) allItems {
	if(allItems == nil) {
		dbg(@"allItems is nil - getting a fresh pack from the DB");
		[self setAllItems: [[db allItems] allObjects]];
	}
	return allItems;
}

- (void) setAllItems:(id) newSetOfItems {
	[allItems release];
	currentItem = nil;
	currentItemIndex = 0;
	allItems = [newSetOfItems retain];
}


- (void) loadItemAtIndex:(int) index {
	dbg(@"Loading item at index: %d", index);
	if(index < 0) {
		currentItem = nil;
		currentItemIndex = 0;
	} else {
		@try{
			[self allItems];
			currentItem = [allItems objectAtIndex: index];
			currentItemIndex = index;
		}
		@catch (NSException *e) {
			NSLog(@"out of range");
			currentItem = nil;
			currentItemIndex = [allItems count] - 1;
		}
	}

	[buttonPrev setEnabled:[self canGoPrev]];

	[self loadItem: currentItem withPositionDescription:[NSString stringWithFormat:@" (%d&nbsp;/&nbsp;%d)", index+1, [allItems count]]];
	[self setButtonStates];
}

- (void) loadItemAtIndex:(int) index fromSet:(id)items {
	[self setAllItems: items];
	[self loadItemAtIndex: index];
}

- (BOOL) canGoNext {
	return currentItemIndex < [allItems count] - 1;
}

- (BOOL) canGoPrev {
	return currentItemIndex > 0;
}

- (void) showCurrentItemInItemList: (id) itemList {
	if(allItems && currentItem) {
		[itemList selectItemWithID: [currentItem google_id]];
	} else {
		dbg(@"no item to showCurrentItemInItemList");
	}
}

- (void) deactivate {
	[self setAllItems: nil];
	[self blacken];
}

- (void) blacken {
	[self loadHTMLString:@"<html><style>body{background-color:#000000;}</style></html>"];
}

- (IBAction) goForward{
	[currentItem userDidScrollPast];
	if([self canGoNext]){
		[self loadItemAtIndex:currentItemIndex + 1];
	} else {
		dbg(@"showing navigation");
		[[[UIApplication sharedApplication] delegate] showNavigation: self];
	}
}

- (IBAction) goBack{
	[self loadItemAtIndex:currentItemIndex - 1];
}

- (void) loadItem: (FeedItem *) item withPositionDescription:(NSString *) position_description{
	NSLog(@"loading item %@", item);
	if(item == nil) {
		[self loadHTMLString:@"<html><body><h1>No More</h1><p>..files for you!</p></body></html>"];
	} else {
		NSString *str = [item htmlForPosition:position_description];
		[self loadHTMLString:str];
	}
	[[self delegate] showSpinner: NO];
}
- (void) loadHTMLString: (NSString *) newHTML {
	[newHTML retain];
	/*
	 // I would love to release the old html, but someone went and broke it - NSNotificationcentre, by the looks of various backtraces...
	 NSLog(@"releasing html: %@", currentHTML);
	 [currentHTML release];
	 */
	currentHTML = newHTML;
	dbg_s(@"HTML is: %@", newHTML);
	[self loadHTMLString:currentHTML baseURL: [NSURL fileURLWithPath: [[appDelegate settings] docsPath]]];
}

- (void)dealloc {
	[self deactivate];
	[db release];
	[super dealloc];
}

- (void) setButtonStates {
	[buttonStar setSelected:  [currentItem is_starred]];
	[buttonShare setSelected: [currentItem is_shared]];
	[buttonRead setSelected:  [currentItem userHasMarkedAsUnread]];
}

- (IBAction) toggleStarForCurrentItem:(id) sender {
	[buttonStar setSelected: [currentItem toggleStarredState]];
}

- (IBAction) toggleSharedForCurrentItem:(id) sender {
	[buttonShare setSelected: [currentItem toggleSharedState]];
}

- (IBAction) toggleReadForCurrentItem:(id) sender {
	[buttonRead setSelected: [currentItem toggleReadState]];
}

- (IBAction) emailCurrentItem:(id) sender {
	NSString * emailURL = [NSString stringWithFormat:@"mailto:?subject=%@&body=%@",
		[@"A link for you!" stringByAddingPercentEscapesUsingEncoding:NSASCIIStringEncoding],
		[[currentItem url]  stringByAddingPercentEscapesUsingEncoding:NSASCIIStringEncoding]
	];
	dbg(@"email url: %@ app=%@", emailURL, [UIApplication sharedApplication]);
	BOOL emailed = [[UIApplication sharedApplication] openURL:[NSURL URLWithString:emailURL]];
	dbg(@"email %s", emailed?"worked":"failed");
}

- (NSString *) currentItemID {
	return [currentItem google_id];
}

@end
