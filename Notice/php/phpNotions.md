# PHP programming language 

PHP is one of the most commonly used languages to generate dynamic websites.

Here are some basic notions about the PHP language, to which I am totally 
new. For more information, see [this lecture](https://youtu.be/OK_JCtrrv-c)
about the PHP language. 


## Getting started  

PHP needs to be run on a web server. In order to create the server that will 
support the code, we must use the following command : 

```
php -S localhost:4000
```

The associated files will be found in the folder `/home/ludivine/www` (on the Linux machine). 

We must generate an HTML skeleton for the file in order for the PHP script to be read and integrated into the web server. 

To write PHP inside an HTML script, we need to use the PHP tag `<?php` at the start of the code and `?>` and the end. 

> At the end of each instruction, we MUST put `;` 


A variable in PHP is identified by a `$`. For instance: 
```
$characterName = "Gloria";  // this is a string
$age = 22;  // this is an integer 
$grade = 16.25;  // this is a decimal or float
$is Hungry = false;  // this is a boolean 
```
We can also encounter `null`, which means that there is no value. 

## Some basic functions 

#### echo 

*echo* enables the PHP code to be printed in the HTML file. We can even include HTML commands into a PHP tag. 

```
echo "test";  // same thing as echo("test")
echo "<p> this is a test </p>";
```

#### String operations 

* *strtolower*: when used on a string, all the letters are lowered;
* *strtoupper*: when used on a string, all the letters become capital letters; 
* *strlen*: returns the length of the string;
*  *strreplace("old_word", "new_word", "string")*: replaces a certain sequence of characters by another; 
*  *substr("string", starting_index, length)*: grabs a part of a given string; 

We can index a string, meaning if we want to know what is character number i of a given string, we must use:
```
$phrase = "This is a phrase";
echo $phrase[0];
```

> In PHP, just like in Python, indexing begins at 0. 


#### Number operations 

* *x%y*: returns the remainer of the division of x by y;
* *$num++ or --*: increments by +1 or -1 the number;
* *pow(x, y)*: returns x^y;
* *floor() and ceil()*: returns the entire part of a number, either to the lower or the upper int  


## Getting user input 

First, we need to set up an HTML form which enables the user to interact with the code:
```
<form action="nameFile.php" method="get> 
  Name: <input type="text" name="name">
  <input type="submit">
</form>
```

* *method* refers to what kind of action we want to perform (here, we want to gather information from the user);
* *input* refers to elements of the site that the user will be able to interact with:
  * `type="text"` creates a textbox 
  * `type="submit"` creates a submit button 

Then, we must get the information from the user in the PHP script: 
```
<?php $_GET["name"] ?>
```

The method `$_GET` is populated by the value that the user submitted on the web page. 

> The information given by the user can be seen in the URL : 
>    `localhost:4000/www/site.php?name="John"`

