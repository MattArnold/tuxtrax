<?php
if(isset($_POST['submit']))
{ 

 $connect = mysqli_connect("mysql.inclusiasm.com", "penguintrax_user", "linttollslooselynative", "penguintrax");
   
  if (!$connect){ die('Could not connect: ' . mysqli_connect_error()); }

  $email = $connect->real_escape_string($_POST["email"]);
  $title = $connect->real_escape_string($_POST["title"]);
  $description = $_POST["description"];
  $duration = $_POST["duration"];
  $setuptime = $_POST["setuptime"];
  $repetition = $_POST["repetition"];
  $comments = $connect->real_escape_string($_POST["comments"]);
  
  $submitter = $connect->real_escape_string($_POST["submitter"]);
  $submitterwords = explode(" ", $submitter);
  $submitterfirstname = array_shift($submitterwords);
  $submitterlastname = implode(" ", $submitterwords);
  
  $person0 = $connect->real_escape_string($_POST["person0"]);
  $person1 = $connect->real_escape_string($_POST["person1"]);
  $person2 = $connect->real_escape_string($_POST["person2"]);
  $person3 = $connect->real_escape_string($_POST["person3"]);
  $person4 = $connect->real_escape_string($_POST["person4"]);
  $person5 = $connect->real_escape_string($_POST["person5"]);
  $person6 = $connect->real_escape_string($_POST["person6"]);
  $person7 = $connect->real_escape_string($_POST["person7"]);

  $resourcerequests = array();
  if (isset($_POST["projector"])) {
	array_push($resourcerequests, "projector");
  } 
  if (isset($_POST["microphone"])) {
	array_push($resourcerequests, "microphone");
  } 
  if (isset($_POST["soundsystem"])) {
	array_push($resourcerequests, "soundsystem");
  } 
  if (isset($_POST["water"])) {
	array_push($resourcerequests, "water");
  } 
  if (isset($_POST["quiet"])) {
	array_push($resourcerequests, "quiet");
  }  

  $enterForm = sprintf("INSERT INTO penguintrax.submissions 
    (Email, Title, Description, Duration, SetupTime, repetition, Comments, FirstName, LastName)
    VALUES ('$email','$title','$description','$duration','$setuptime','$repetition','$comments','$submitterfirstname', '$submitterlastname')");

	echo $enterForm;

  $result = $connect->query($enterForm);
  if ($result) {
	echo "Successfully ran query.";
	$submission_id = $connect->insert_id;
	foreach($resourcerequests as $r) {
		$result = $connect->query("SELECT Id FROM penguintrax.resources WHERE LOWER(Name) = LOWER('$r');");
		if ($result->num_rows) {
			$resultobj = $result->fetch_object();
			$result = $connect->query("INSERT INTO penguintrax.submit_resource_requests (SubmissionId, ResourceId, Quantity) VALUES ('$submission_id', '$resultobj->Id', '1');");
			echo $connect->error;
			//$result->close();
			echo "Found resource: $r\r\n";
		} else {
			echo "Could not find resource: $r\n";
		}
		//$result->close();
	}
  } else {
	echo "Error: " . $connect->error;
  }

  $connect->close();

 }
else {
	echo "You got here in error!";
}
?>