var loadFile = function(event) {
    var output = document.getElementById('output');
    output.src = URL.createObjectURL(event.target.files[0]);
    output.onload = function() {
        URL.revokeObjectURL(output.src) // free memory
    }
};
// ************************** THE PAGE REFRESH ********************** //
window.addEventListener('DOMContentLoaded', (event) => {
    // Call the settingDefault when the page is refresh
    if (typeof settingDefault  === "function") {
        settingDefault();
    } if (document.getElementsByClassName("is-active-class")[0]) {
         if (!document.getElementsByClassName("is-active-class")[0].checked) {
             document.getElementsByClassName("last-date-class")[0].disabled = true;
             document.getElementsByClassName("last-date-class")[0].addClass='opacity-low';
    //       document.getElementsByClassName("checked_as-inactive")[0].disabled = true;
    //       console.log("document.getElementsByClassName::: ", document.getElementsByClassName("checked_as-inactive")[0]);
        }
    } if (document.getElementsByClassName('start-date-class').length || document.getElementsByClassName('end-date-class').length) {
        onstartDateChange('onloading');
    }
 })

function settingDefault () {
    var el = document.getElementById("salary_complete_details");
    if ( document.getElementById("select-employment_type") ) {
        var emp_type = parseInt(document.getElementById("select-employment_type").value);
        var hourly_details = document.getElementById("hourly_pay_details");
        if ( emp_type == 1000 ) {
                el.style.display = 'block'
                hourly_details.style.display = 'none'
        } else {
            el.style.display = 'none'
            hourly_details.style.display = 'block'
        }
    }
}

function  employee_type_function() {
    var el = document.getElementById("salary_complete_details");
    if ( document.getElementById("select-employment_type") ) {
        var emp_type = parseInt(document.getElementById("select-employment_type").value);
        var hourly_details = document.getElementById("hourly_pay_details");
        if ( emp_type == 1000 ) {
                el.style.display = 'block'
                hourly_details.style.display = 'none'
                document.getElementById("hourlyRateId").value = ''
                document.getElementById("salaryId").value = ''
        } else {
            el.style.display = 'none'
            hourly_details.style.display = 'block'
            document.getElementById("salaryId").value = ''
            document.getElementById("hourlyRateId").value = ''
        }
    }
}

function newEmployeeValidation () {

    if (document.getElementById("select-employment_type") ) {
        console.log("SALERt: ", document.getElementById("salaryId"));
        console.log("SALERt: ", document.getElementById("bonusId"));
        console.log("SALERt: ", document.getElementById("basicAllowanceId"));
        console.log("SALERt: ", document.getElementById("medicalAllowanceId"));
        console.log("SALERt: ", document.getElementById("pfId"));
        console.log("SALERt: ", document.getElementById("taxId"));
        console.log("SALERt: ", document.getElementById("hourlyRateId"));
    }
}

// Scroll to the top
window.onscroll = function(ev) {
    if (document.getElementById("back-to-top")) {
        if ((window.scrollY) > 100 ) {
            document.getElementById("back-to-top").style.display = "block";
        } else {
            document.getElementById("back-to-top").style.display = "none";
        }
    }
};

function roleChange ( role) {
    console.log("1312321: ", role);
}

function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2)
        month = '0' + month;
    if (day.length < 2)
        day = '0' + day;

    return [year, month, day].join('-');
}

console.log(formatDate('Sun May 11,2014'));

function isActiveCheck () {
    if (!document.getElementsByClassName("is-active-class")[0].checked) {
         document.getElementsByClassName("last-date-class")[0].value = formatDate(new Date());
         document.getElementsByClassName("last-date-class")[0].disabled = true;
         document.getElementsByClassName("last-date-class")[0].addClass='opacity-low';
//         document.getElementsByClassName("checked_as-inactive")[0].disabled = true;
    } else {
        document.getElementsByClassName("last-date-class")[0].value = '';
        document.getElementsByClassName("last-date-class")[0].disabled = false;
//        document.getElementsByClassName("checked_as-inactive")[0].disabled = false;
    }
}

function onstartDateChange (onloading) {
    document.getElementsByClassName('end-date-class')[0].setAttribute('min', document.getElementsByClassName('start-date-class')[0].value)
    !onloading ?  document.getElementById("end-date-event").value = document.getElementById("start-date-event").value : false
}

function callRadioEmployee (value) {
    console.log("RSDIO");
    valueActive = {
        valueActive: value
    }
      var xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
//        window.location.href = window.location.href + '/EmployeeActive'
          console.log("Ready me: ", window.location.href);
//          window.location.href = ''
        }
      };
      xhttp.open("POST", "EmployeeActive", true);
      xhttp.setRequestHeader("Content-type", "application/json");
      xhttp.send(JSON.stringify(valueActive));


//    var request = new XMLHttpRequest()
//    console.log("window.location.href : ", window.location.href );
//    var locationHref = window.location.href
//    if ( locationHref.indexOf('EmployeeActive') != -1 ) {
//    console.log("**************");
//        window.location.href = locationHref.split("EmployeeActive")[0]
//    }
//    request.open('GET', 'EmployeeActive/'+ value, true)
//    request.onload = function () {
//      // Begin accessing JSON data here
//      console.log("RESPONSE: ", window.location.href);
//      window.location.href = window.location.href + 'EmployeeActive/'+ value
////      var data = JSON.parse(this.response)
////
////      if (request.status >= 200 && request.status < 400) {
////        data.forEach((movie) => {
////          console.log(movie.title)
////        })
////      } else {
////        console.log('error')
////      }
//    }
//
//    request.send()

}



