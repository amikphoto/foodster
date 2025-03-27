(function(fn) {
	'use strict';
	fn(window.jQuery, window, document);
}(function($, window, document) {
	'use strict';

	$(function() {
		$('.sort-btn').on('click', '[data-sort]', function(event) {
			event.preventDefault();

			var $this = $(this),
				sortDir = 'down';

			if ($this.data('sort') !== 'up') {
				sortDir = 'up';
			}

			$this.data('sort', sortDir).find('.bi').attr('class', 'bi bi-sort-' + sortDir);

			// call sortDesc() or sortAsc() or whathaveyou...
			// test
		});
	});
}));