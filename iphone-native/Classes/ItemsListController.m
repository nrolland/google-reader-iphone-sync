#import "ItemsListController.h"

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

@end
