if (document.getElementById('id_emailBackend') != null) { //only in case the item appears on the page to prevent from errors
    $(document).ready(function () { //function will wait for the page to fully load before executing
        if (document.getElementById('id_emailBackend').value != 'django.core.mail.backends.smtp.EmailBackend') {
            //disable all fields
            $("#id_emailHost").prop('disabled', true);
            $("#id_emailHostUser").prop('disabled', true);
            $("#id_emailHostPassword").prop('disabled', true);
            $("#id_emailHostPort").prop('disabled', true);
            $("#id_emailUseTLS").prop('disabled', true);
         }
         if (document.getElementById('id_emailBackend').value == 'django.core.mail.backends.filebased.EmailBackend') {
            $("#id_emailFilePath").prop('disabled', false);
            $("#id_emailFilePath").prop('required', true);
         } else {
            $("#id_emailFilePath").prop('disabled', true);
            $("#id_emailFilePath").prop('required', false);
         }
         $("select[name=emailBackend]").change(function () { //specifying onchange function for selectbox
     //       console.log("Change detected!")
            if (this.value == "django.core.mail.backends.smtp.EmailBackend") { //if the new value is usual smtp email
                $("#id_emailHost").prop('disabled', false);//would recommend readonly instead of disable for form integrity
                $("#id_emailHostUser").prop('disabled', false);
                $("#id_emailHostPassword").prop('disabled', false);
                $("#id_emailHostPort").prop('disabled', false);
                $("#id_emailUseTLS").prop('disabled', false);
            }else{ //if the new value is anything else
                $("#id_emailHost").prop('disabled', true);
                $("#id_emailHostUser").prop('disabled', true);
                $("#id_emailHostPassword").prop('disabled', true);
                $("#id_emailHostPort").prop('disabled', true);
                $("#id_emailUseTLS").prop('disabled', true);
            }
            if (this.value == 'django.core.mail.backends.filebased.EmailBackend') {
                $("#id_emailFilePath").prop('disabled', false);
                $("#id_emailFilePath").prop('required', true);
            } else {
                $("#id_emailFilePath").prop('disabled', true);
                $("#id_emailFilePath").prop('required', false);
            }
        });
    });
};