



jQuery.cometSettings = {
   interval: false, 
   pos: 0, 
   active: false 
};

jQuery.cometStop = function() {
   jQuery.cometSettings.active = false;
};

jQuery.cometStart = function(url, options, callback) {

   if(jQuery.isFunction(options)) {
      callback = options;
   }
   
   jQuery.cometSettings.pos = 0;
   
   if(jQuery.browser.msie) {
      
      var doc = new ActiveXObject('htmlfile');
      doc.open();
      doc.write('<html>');
      doc.write('<html>');
      doc.write('<script>document.domain = \'' + document.domain + '\'');
      doc.write('</html>');
      doc.close();
      var div = doc.createElement('DIV');
      doc.appendChild(div);
      
      div.innerHTML = '<iframe name=\'ifr\' src=\'' + url + '\'></iframe>';
      jQuery.cometSettings.active = true;
      
      if(! jQuery.cometSettings.interval) {
         jQuery.cometSettings.interval = setInterval( function() {
            
            var xmlhttp = doc.frames['ifr'].document;

            if(xmlhttp.readyState == 'complete') {
               clearInterval(jQuery.cometSettings.interval);
               jQuery.cometSettings.interval = false;
         
               if(jQuery.cometSettings.active)   {
                  jQuery.cometStart(url, options, callback);
               }
            }
            
            var data; 
            try {
               data = xmlhttp.firstChild.innerHTML;
            }
            catch(error) {
               return;
            }
            
            data = data.substr(jQuery.cometSettings.pos);

            if(data.indexOf('<SCRIPT>') < 0) {
               return;
            }

            var start = data.indexOf('<SCRIPT>') + 8;
            var stop = data.indexOf('</SCRIPT>') - start;
            data = data.substr(start, stop);

            debug(data);

            try {
               eval('data = ' + data);
            }
            catch(error) {
            }

            callback(data);
         
            jQuery.cometSettings.pos = jQuery.cometSettings.pos + start + 8 + stop - 1;
      
         }, 250 );
      }
   }
   else if(jQuery.browser.mozilla) {
      
      var xmlhttp = new XMLHttpRequest();
      xmlhttp.onreadystatechange = function() {
         
         if(xmlhttp.readyState == 4 && jQuery.cometSettings.active) {
            jQuery.cometStart(url, options, callback);
            return(false);
         }
         
         if(xmlhttp.readyState == 3) {
            var data = xmlhttp.responseText;
            
            data = data.substr(jQuery.cometSettings.pos);
            
            if(data.indexOf('<script>') < 0) {
               return(false);
            }
            
            var start = data.indexOf('<script>') + 8;
            var stop = data.indexOf('</script>') - start;
            data = data.substr(start, stop);

            debug(data);
            
            try {
               eval('data = ' + data);
            }
            catch(error) {
            }

            callback(data);

            jQuery.cometSettings.pos = jQuery.cometSettings.pos + start + 8 + stop;
         }
      };
      xmlhttp.open('GET', url, true);
      xmlhttp.send(null);
      jQuery.cometSettings.active = true;
   }
   else if(jQuery.browser.opera) {
      
      var xmlhttp = new XMLHttpRequest();
      xmlhttp.onreadystatechange = function() {

         if(xmlhttp.readyState == 4) {
            
            clearInterval(jQuery.cometSettings.interval);
            jQuery.cometSettings.interval = false;

            if(jQuery.cometSettings.active)   {
               jQuery.cometStart(url, options, callback);
            }
         }
         if(xmlhttp.readyState == 3) {
            if(! jQuery.cometSettings.interval) {
               
               jQuery.cometSettings.interval = setInterval( function() {
                     
                  var data = xmlhttp.responseText;
                  data = data.substr(jQuery.cometSettings.pos);

                  if(data.indexOf('<script>') < 0) {
                     return(false);
                  }
                  
                  var start = data.indexOf('<script>') + 8;
                  var stop = data.indexOf('</script>');
                  data = data.substring(start, stop);
                  
                  jQuery.cometSettings.pos = jQuery.cometSettings.pos + stop + 1;
                  
                  // alert(jQuery.cometSettings.pos + ' (' + start + ',' + stop + ') = ' + data);
                  
                  debug(data);

                  try {
                     data = eval(' data = ' + data);
                  }
                  catch(error) {
                     alert(error);
                  };
                  
                  callback(data);
         
               }, 250 );
            }
         }
      };
      xmlhttp.open('GET', url, true);
      xmlhttp.send(null);
      jQuery.cometSettings.active = true;
   }
   else if(jQuery.browser.safari) {
      alert('I would love to have this work in Safari.  If you know how to do it, let me know.');
   }
   else {
      alert('You should take this opportunity to find what is necessary to implement a comet solution in this browser.');
   }

   function debug(data) {
      
      if(typeof(options) == 'object' && jQuery(options.debug)) {
         jQuery(options.debug).prepend(data + '<br><br>');
      }
   }
};





