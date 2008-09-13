#import "ItemListController.h"
#import "TCHelpers.h"

@implementation ItemListController
- (void) setDB: (id) db {
	[dataSource setDB: db];
	[listView reloadData];
}

- (void) selectItemWithID:(NSString *) google_id {
	id indexPath = [dataSource getIndexPathForItemWithID:google_id];
	[listView selectRowAtIndexPath:indexPath animated:NO scrollPosition:UITableViewScrollPositionTop];
}

- (void) selectItemWithID: (NSString *) google_id inItemSet: (id) set {
	[self setItemSet: set];
	[self selectItemWithID: google_id];
}

- (IBAction) toggleOptions:(id)sender {
	[self hideOptions] || [self showOptions];
}

- (BOOL) showOptions {
	BOOL didShow = NO;
	if(!optionsAreVisible) {
		[showHideOptionsButton setTitle:@"Done"];
		[optionsView setHidden:NO];
		[optionsView animateFadeIn];
		optionsAreVisible = YES;
		didShow = YES;
	}
	return didShow;
}

- (BOOL) optionsDidFadeOut {
	[optionsView setHidden:YES];
}

- (BOOL) hideOptions {
	BOOL didHide = NO;
	if(optionsAreVisible) {
		[showHideOptionsButton setTitle:@"Options"];
		[optionsView animateFadeOutThenTell:self withSelector:@selector(optionsDidFadeOut)];
		optionsAreVisible = NO;
		[self refresh: self];
		didHide = YES;
	}
	return didHide;
}

- (void) redraw{
	dbg(@"redrawing listview");
	[listView reloadData];
}

-(IBAction) refresh: (id) sender {
	[self hideOptions];
	[dataSource reloadItems];
	[self redraw];
}

- (IBAction) markAllItemsAsRead:   (id) sender { [self markAllItemsWithReadState: YES]; }
- (IBAction) markAllItemsAsUnread: (id) sender { [self markAllItemsWithReadState: NO];  }

- (void) markAllItemsWithReadState: (BOOL) read {
	alertWasForMarkingAsRead = read;
	markAsReadAlert = [[UIAlertView alloc]
		initWithTitle: [NSString stringWithFormat: @"Mark as %@",read ? @"read":@"unread"]
		message: [NSString stringWithFormat:@"Do you really want to mark ALL items as %@?", read ? @"read":@"unread"]
		delegate: self
		cancelButtonTitle: @"Cancel"
		otherButtonTitles: @"OK", nil];
	[markAsReadAlert show];
}

- (void) alertView:(id)view clickedButtonAtIndex:(NSInteger) index {
	dbg(@"answer: %d", index);
	if(index == 1 && view == markAsReadAlert) {
		[dataSource setAllItemsReadState: alertWasForMarkingAsRead];
		[dataSource reloadItems];
		[self hideOptions];
	}
	[view release];
}

@end
