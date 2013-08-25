(function($){
	$.fn.uxmessage = function(kind, text) {
	  if (text.length > 80) {
	    text = text.slice(0,100) + '\n...'
	  }
	  
  	if (kind == 'notice') {
  		$('#log_content').prepend('<div class="log_item log_notice well" style="display:none">' + text + '</div>');
  		$('#log_content').children('div').first().show('blind');
  		if ($("#log_content").is(':hidden')) {
    		$().toastmessage('showNoticeToast', text);
    	}
  	} else if (kind == 'success') {
  		$('#log_content').prepend('<div class="log_item log_success well" style="display:none">' + text + '</div>');
  		$('#log_content').children('div').first().show('blind');
  		if ($("#log_content").is(':hidden')) {
    		$().toastmessage('showSuccessToast', text);		
      }
  	} else if (kind == 'warning') {
  		$('#log_content').prepend('<div class="log_item log_warning well" style="display:none">' + text + '</div>');
  		$('#log_content').children('div').first().show('blind');
  		if ($("#log_content").is(':hidden')) {
    		$().toastmessage('showWarningToast', text);		
    	}
  	} else if (kind == 'error') {
  		$('#log_content').prepend('<div class="log_item log_error well" style="display:none">' + text + '</div>');
  		$('#log_content').children('div').first().show('blind');
  		if ($("#log_content").is(':hidden')) {
    		$().toastmessage('showErrorToast', text);		
    	}
  	}

  	while ($('#log_content').children('div').length > 200) {
  	  $('#log_content').children('div').last().remove();
  	}

	};
})(jQuery); 

$(document).ready(function(){
	
$('#imageFile').change(function(){
    var file = this.files[0];
    name = file.name;
    size = file.size;
    type = file.type;
    //Your validation
});

function getFileName(url){
	var pos = url.lastIndexOf("/");
	if(pos == -1){
	   pos = url.lastIndexOf("\\")
	}
	var filename = url.substr(pos +1)
	return filename;
}

$("#fileUpload").change(function () {
    fileName = getFileName(jQuery(this).val())
    //alert(fileName)
	$('#fileName').attr("value", fileName);
});

  $("#gcode_submit").click(function(e) {
  	// send gcode string to server via POST
  	var gcode = $('#gcode_program').val();
    send_gcode(gcode, "G-Code sent to backend.", true);
  	return false;
  });

  $('#gcode_save_to_queue').tooltip();
  $("#gcode_save_to_queue").click(function(e) {
    save_and_add_to_job_queue($.trim($('#gcode_name').val()), $('#gcode_program').val());
    return false;
  });
  
  // populate queue from queue directory
	  $.getJSON("/queue/list", function(data) {
		$.each(data, function(index, name) {
		   $('#command_list_queue').prepend('<li><a href="/library/'+name+'">'+ name +'</a></li>')
		});
	  });
  // populate library from library directory
  $.getJSON("/library/list", function(data) {
    if (typeof(data.sort) == 'function') {
      data.sort();
    }
    $.each(data, function(index, name) {
      $('#gcode_library').prepend('<li><a href="/library/'+ name + '">'+ name +'</a></li>');
    }); 	
  });
  // .success(function() { alert("second success"); })
  // .error(function() { alert("error"); })
  // .complete(function() { alert("complete"); });
});  // ready


 function sendToBackend() {
 
    
    // reset file input form field so change event also triggers if
    // same file is chosen again (but with different dpi)
    $('#svg_upload_file_temp').val($('#svg_upload_file').val())
    $('#svg_upload_file').val('')

    var filedata = e.target.result;
    var fullpath = $('#svg_upload_file_temp').val();
    var filename = fullpath.split('\\').pop().split('/').pop();
    var ext = filename.slice(-4);
    if (ext == '.svg' || ext == '.SVG') {
      $().uxmessage('notice', "parsing SVG ...");
    } else if (ext == '.dxf' || ext == '.DXF') {
      $().uxmessage('notice', "parsing DXF ...");
      $().uxmessage('warning', "DXF import is limited to R14, lines, arcs, lwpolylines, and mm units");
    }
    if (filedata.length > 102400) {
      $().uxmessage('notice', "Importing large files may take a few minutes.");
    }
    $.ajax({
      type: "POST",
      url: "/image",
      data: {'filename':filename,'filedata':filedata},
      dataType: "json",
      success: function (data) {
        // alert(JSON.stringify(data));
        handleParsedGeometry(data);
      },
      error: function (data) {
        alert("Error!");
      },
      complete: function (data) {
        alert("Done!" );
      }
    });
  }
 

function send_gcode(gcode, success_msg, progress) {
  if (1) {
    if (typeof gcode === "string" && gcode != '') {
      $.ajax({
        type: "POST",
        url: "/gcode",
        data: {'command_program':gcode},
		contentType:"application/x-www-form-urlencoded; charset=utf-8",
        // dataType: "json",
        success: function (data) {
          if (data == "__ok__") {
            $().uxmessage('success', success_msg);
            if (progress = true) {
              // show progress bar, register live updates
              if ($("#progressbar").children().first().width() == 0) {
                $("#progressbar").children().first().width('5%');
                $("#progressbar").show();
                var progress_not_yet_done_flag = true;
                var progresstimer = setInterval(function() {
                  $.get('/queue_pct_done', function(data2) {
                    if (data2.length > 0) {
                      var pct = parseInt(data2);
                      $("#progressbar").children().first().width(pct+'%');                
                    } else {
                      if (progress_not_yet_done_flag) {
                        $("#progressbar").children().first().width('100%');
                        $().uxmessage('notice', "Done.");
                        progress_not_yet_done_flag = false;
                      } else {
                        $('#progressbar').hide();
                        $("#progressbar").children().first().width(0); 
                        clearInterval(progresstimer);
                      }
                    }
                  });
                }, 2000);
              }
            }
          } else {
            alert("Error!" );
          }
        },
        error: function (data) {
          alert("Error!" );
        },
        complete: function (data) {
          alert("Done!" );
        }
      });
    } else {
      $().uxmessage('error', "No gcode.");
    }
  } else {
    $().uxmessage('warning', "Not ready, request ignored.");
  }
}



 
