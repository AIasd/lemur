
$(document).ready(function(){
    //Modify an existing lab
    $('.modifyLab').click(function(){
        var labId = $(this).closest('tr').data('labid');
        window.location.replace('/admin_modify_lab/'+labId);        
    });
    
    // The reason that we use javascript to show the modal rather than html is that this enables us
    // to show the modal that is closest to the delete button such that the modal is within the tr
    // that we want to delete
    $('.deleteLab').click(function(){
        $(this).closest('tr').find('#deleteConfirm').modal("show");
    });

    //Duplicate/Delete a lab
    $('.duplicateLab').add($('button[name=confirm]')).click(function(){
        var operation = $(this).data('operation');
        var labId = $(this).closest('tr').data('labid');
        //Communicate the name of the lab to be duplicated with python via Ajax 
        $.ajax({
          type: 'POST',
          contentType: 'application/json',
          dataType: 'json',
          url: 'http://127.0.0.1:5000/_admin_'+operation,
          data: JSON.stringify({'labId':labId}),
          success: function(result){
                    console.log(operation+' successfully');               
                },
          error : function(result){
                    err_msg = JSON.parse(result.responseText)['data'];
                    $('#errorMsgs').html('Fail to duplicate lab<br>'+err_msg);
                    $('#errorPopup').modal("show");
                    console.log('Fail to '+operation);
                    console.log(result);
                    console.log('url: '+'http://127.0.0.1:5000/_admin_'+operation);
                    console.log('labId: '+labId);
                }
        });
        if (operation=='delete_lab'){
            $(this).closest('tr').remove();
        }

        location.reload();

    });

    //Change a lab's status
    $('.makeDownloadOnly').add($('.activateLab')).add($('.deactivateLab')).click(function(){
        var labId = $(this).closest('tr').data('labid');
        var statusClassName = $(this).attr('class')
        var newStatus = 'Activated';
        if (statusClassName=='makeDownloadOnly'){
            newStatus = 'Downloadable';
        }
        else if (statusClassName=='activateLab'){
            newStatus = 'Activated';
        }
        else if (statusClassName=='deactivateLab'){
            newStatus = 'Unactivated';
        }
        //Communicate the name of the lab to be duplicated with python via Ajax 
        $.ajax({
          type: 'POST',
          contentType: 'application/json',
          dataType: 'json',
          url: 'http://127.0.0.1:5000/_admin_change_lab_status/'+newStatus,
          data: JSON.stringify({'labId':labId}),
          success: function(result){
                    console.log('Change status successfully');
                },
          error : function(result){
                    err_msg = JSON.parse(result.responseText)['data'];
                    $('#errorMsgs').html('Fail to change status<br>'+err_msg);
                    $('#errorPopup').modal("show");
                    console.log('Fail to change lab status');
                    console.log(result);
                    console.log('url: '+'http://127.0.0.1:5000/_admin_change_status/'+newStatus);
                    console.log('labid: '+labId);
                }
        });
        location.reload();   
    });

});
