#import "ItemsListController.h"
#import "tcHelpers.h"

@implementation ItemsListController
- (void) setItemSet: (id) set {
	[dataSource setItemSet: set];
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
		optionsAreVisible = YES;
		didShow = YES;
	}
	return didShow;
}

- (BOOL) hideOptions {
	BOOL didHide = NO;
	if(optionsAreVisible) {
		[showHideOptionsButton setTitle:@"Options"];
		[optionsView setHidden:YES];
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

@end
