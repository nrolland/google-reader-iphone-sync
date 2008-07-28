#import "tcWebView.h"
#import "tcDirList.h"

@implementation tcWebView
- (void) load {
	NSLog(@"loading db");
	db = [[[tcItemDB alloc] initWithPath: @"/Users/tim/Documents/Programming/Python/reader/working/entries_copy.sqlite"] retain];
	NSLog(@"loading item");
	[self loadUnread];
}

- (IBAction) loadUnread {
	[allItems release];
	allItems = [[[db allItems] allObjects] retain];
	[self loadItemAtIndex:0];
}

- (void) loadItemAtIndex:(int) index {
	NSLog(@"Loading item at index: %d", index);
	if(index < 0) {
		currentItem = nil;
		currentItemIndex = 0;
	} else {
		@try{
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

	NSLog(@"loading item at index: %d", currentItemIndex);
	[self loadItem: currentItem];
	[self setButtonStates];
}

- (BOOL) canGoNext {
	return currentItemIndex < [allItems count] - 1;
}

- (BOOL) canGoPrev {
	return currentItemIndex > 0;
}

- (void) deactivate {
	if(!([self canGoNext] && [self canGoPrev])) {
		[currentItem userDidScrollPast];
	}
}

- (IBAction) goForward{
	NSLog(@"FWD");
	[self loadItemAtIndex:currentItemIndex + 1];
}

- (IBAction) goBack{
	NSLog(@"back");
	[self loadItemAtIndex:currentItemIndex - 1];
}

- (void) loadItem: (id) item {
	NSLog(@"loading item %@", item);
	[currentItem userDidScrollPast];
	if(item == nil) {
		[self loadHTMLString:@"<html><body><h1>No More</h1><p>..files for you!</p></body></html>"];
	} else {
		NSString *str = [item html];
//		NSLog(@"html str: %@", str);
		[self loadHTMLString:str];
		NSLog(@"done");
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
	[self loadHTMLString:currentHTML baseURL: [NSURL fileURLWithPath: @"file://localhost/Users/tim/Documents/Programming/Python/reader/working/entries/"]];
}

- (void)dealloc {
	[db release];
	[super dealloc];
}

- (void) setButtonStates {
	[buttonStar setSelected: [currentItem is_starred]];
	[buttonRead setSelected: [currentItem userHasMarkedAsRead]];
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
