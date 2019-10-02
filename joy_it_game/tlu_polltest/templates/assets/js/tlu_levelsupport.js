var sPath = window.location.pathname;
//var sPage = sPath.substring(sPath.lastIndexOf('\\') + 1);
var sPageNum = sPath.substring(sPath.lastIndexOf('/') + 1);
var lastSlashPos=sPath.lastIndexOf('/')
var sPage = sPath.substring(sPath.lastIndexOf('/',lastSlashPos-1) + 1);
console.log(sPage)
if (sPage.includes('start')) {
    var glob_data = null
    console.log ("Timeout included")
    var delay_ms=1000
	$(document).ready(function(){ //wait for page got loaded...
		(function worker() {
	        jQuery.ajax({
	            url: '/tlu_polltest/ajax/level_update/',
	            data: {
                    'level':sPageNum
		        },
	            dataType: 'json',
			    success: function(data) {
                    glob_data=data
                    delay_ms=data.delay_ms
                    $('#status').html(data.info)
                    $('#current_progress').html(data.current_progress+'%')
                    $('#current_progress').attr('aria-valuenow',data.current_progress)
                    $('#current_progress').attr('style','width: '+data.current_progress+'%')
                    $('#overall_progress').html(data.overall_progress+'%')
                    $('#overall_progress').attr('aria-valuenow',data.overall_progress)
                    $('#overall_progress').attr('style','width: '+data.overall_progress+'%')
                    $('#startbutton').html(data.button_text)
                    $('#startbutton').attr('href',data.button_url)
					console.log( data )
			    },    complete: function() {
                    // Schedule the next request when the current one's complete  
                    if ((glob_data != null) && (glob_data.poll > 0)) {
                        setTimeout(worker, delay_ms);
                    }
 	 	        }
 	        });
 	    })();
	});    
}