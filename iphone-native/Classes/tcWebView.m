#import "tcWebView.h"
#import "tcDirList.h"
#import "tcHelpers.h"

@implementation tcWebView
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
	dbg(@"setting allItems to: %@", newSetOfItems);
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
	[buttonNext setEnabled:[self canGoNext]];

	[self loadItem: currentItem];
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
		dbg(@"selectingItem from %@", allItems);
		[itemList selectItemWithID: [currentItem google_id] inItemSet: allItems];
	} else {
		dbg(@"no item to showCurrentItemInItemList");
	}
}

- (void) deactivate {
	if(!([self canGoNext] && [self canGoPrev])) {
		[currentItem userDidScrollPast];
	}
	[self setAllItems: nil];
	[self loadHTMLString:@""];
}

- (IBAction) goForward{
	NSLog(@"FWD");
	[currentItem userDidScrollPast];
	[self loadItemAtIndex:currentItemIndex + 1];
}

- (IBAction) goBack{
	NSLog(@"back");
	[currentItem userDidScrollPast];
	[self loadItemAtIndex:currentItemIndex - 1];
}

- (void) loadItem: (tcItem *) item {
	NSLog(@"loading item %@", item);
	if(item == nil) {
		[self loadHTMLString:@"<html><body><h1>No More</h1><p>..files for you!</p></body></html>"];
	} else {
		NSString *str = [item html];
		[self loadHTMLString:str];
	}
}
- (void) loadHTMLString: (NSString *) newHTML {
	[newHTML retain];
	/*
	 // I would love to release the old html, but someone went and broke it - NSNotificationcentre, by the looks of various backtraces...
	 NSLog(@"releasing html: %@", currentHTML);
	 [currentHTML release];
	 */
	currentHTML = newHTML;
	[self loadHTMLString:currentHTML baseURL: [NSURL fileURLWithPath: @"/Users/tim/Documents/Programming/Python/reader/working/entries/"]];
}

- (void)dealloc {
	[self deactivate];
	[db release];
	[super dealloc];
}

- (void) setButtonStates {
	[buttonStar setSelected: [currentItem is_starred]];
	[buttonRead setSelected: [currentItem userHasMarkedAsUnread]];
}

- (IBAction) toggleStarForCurrentItem:(id) sender {
	[buttonStar setSelected: [currentItem toggleStarredState]];
}

- (IBAction) toggleReadForCurrentItem:(id) sender {
	[buttonRead setSelected: [currentItem toggleReadState]];
}

// TODO...
- (IBAction) emailCurrentItem:(id) sender {}



@end
