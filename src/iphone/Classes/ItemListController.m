#import "ItemListController.h"
#import "TCHelpers.h"

@implementation ItemListController
- (id) initWithDelegate: (id) _delegate {
	self = [super init];
	[self setDelegate: _delegate];
	return self;
}

- (id) title {
	NSString * title = [delegate tag];
	if(!title) {
		title = @"[no tag]";
	}
	return title;
}

- (void) setListView: (id) _listView {
	[_listView retain];
	[listView release];
	listView = _listView;
}

- (void) setDB: (id) db {
	[[self delegate] setDB: db];
	[listView reloadData];
}
- (id) delegate {
	return delegate;
}

- (id) listView { return listView; }

- (void) setDelegate: (id) _delegate {
	[_delegate retain];
	[delegate release];
	delegate = _delegate;
}

- (void) selectItemWithID:(NSString *) google_id {
	id indexPath = [[self delegate] getIndexPathForItemWithID:google_id];
	if(indexPath) {
		[listView selectRowAtIndexPath:indexPath animated:NO scrollPosition:UITableViewScrollPositionTop];
	}
}

- (void) redraw{
	dbg_s(@"redrawing listView");
	[listView reloadData];
}

-(IBAction) refresh: (id) sender {
	[delegate reloadItems];
	[listView reloadData];
	[self redraw];
	[listView setNeedsDisplay]; // this shouldn't be necessary, surely...
}

- (IBAction) markItemsAsRead:   (id) sender { [self markAllItemsWithReadState: YES]; }
- (IBAction) markItemsAsUnread: (id) sender { [self markAllItemsWithReadState: NO];  }

- (void) markItemsWithReadState: (BOOL) read {
	alertWasForMarkingAsRead = read;
	markAsReadAlert = [[UIAlertView alloc]
		initWithTitle: [NSString stringWithFormat: @"Mark as %@",read ? @"read":@"unread"]
		message: [NSString stringWithFormat:@"Do you really want to mark ALL items as %@?", read ? @"read":@"unread"]
		delegate: self
		cancelButtonTitle: @"Cancel"
		otherButtonTitles: @"OK", nil];
	[markAsReadAlert show];
}

- (void) alertView:(id)_view clickedButtonAtIndex:(NSInteger) index {
	if(index == 1 && _view == markAsReadAlert) {
		[[self delegate] setAllItemsReadState: alertWasForMarkingAsRead];
		[[self delegate] reloadItems];
		[[[UIApplication sharedApplication] delegate] refreshItemLists];
	}
	[_view release];
}

@end
