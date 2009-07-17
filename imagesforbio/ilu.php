<?php

function leer($url)
{
	//fixed Disabling of ilu.php email bug
	$f = fopen($url,"r"); 

	$data="";

	/*$c=0;
	while(!feof($f)){ 
		$data.= fgets($f);
		$c+=1;
		if ($c>100){
			$data="";
			break;
		}
	}*/
	
	$data=stream_get_contents($f);
	
	fclose($f);
	
	return $data;
}

function myurlencode ( $t ) {
	$t = str_replace ( " " , "_" , $t ) ;
	$t = urlencode ( $t ) ;
	return $t ;
}

function get_edit_timestamp ( $lang , $project , $title ) {
	$t=leer("http://$lang.wikipedia.org/w/api.php?action=query&prop=revisions&titles=".str_replace(" ", "_", $title)."&rvlimit=1&rvprop=timestamp&format=xmlfm");
	
	$t = explode ( 'timestamp=&quot;' , $t , 2 ) ;
	$t = explode ( '&quot;' , array_pop ( $t ) , 2 ) ;
	$t = array_shift ( $t ) ;
	$t = str_replace ( '-' , '' , $t ) ;
	$t = str_replace ( ':' , '' , $t ) ;
	$t = str_replace ( 'T' , '' , $t ) ;
	$t = str_replace ( 'Z' , '' , $t ) ;
	return $t ;
}

function cGetEditButton ( $text , $title , $lang , $project , $summary , $button_label , $new_window = true , $add = false , $diff = false , $minor = false ) {
	
	$t = get_edit_timestamp ( $lang , $project , $title ) ;
	$timestamp = $t ;
	
	$text = htmlspecialchars ( $text, ENT_QUOTES ) ;
	$summary = htmlspecialchars ( $summary, ENT_QUOTES) ;

	$url = "http://{$lang}.{$project}.org/w/index.php?title=" . myurlencode ( $title ) . '&action=edit' ;
	if ( $add ) $url .= '&section=new' ;
	$ncb = "<form id='upload' method=post enctype='multipart/form-data'" ;
	if ( $new_window ) $ncb .= " target='_blank'" ;
	$ncb .= " action='{$url}' style='display:inline'>" ;
	$ncb .= "<input type='hidden' name='wpTextbox1' value='{$text}'/>" ;
	$ncb .= "<input type='hidden' name='wpSummary' value='{$summary}'/>" ;
	if ( $diff ) $ncb .= "<input type='hidden' name='wpDiff' value='wpDiff' />" ;
	else $ncb .= "<input type='hidden' name='wpPreview' value='wpPreview' />" ;
	
	$starttime = date ( "YmdHis" , time() + (12 * 60 * 60) ) ;
	$ncb .= "<input type='hidden' value='{$starttime}' name='wpStarttime' />" ;
	$ncb .= "<input type='hidden' value='{$t}' name='wpEdittime' />" ;

  if ( $minor ) $ncb .= "<input type='hidden' value='1' name='wpMinoredit' />" ;
	if ( $diff ) $ncb .= "<input type='submit' name='wpDiff' value='$button_label'/>" ;
	else $ncb .= "<input type='submit' name='wpPreview' value='$button_label'/>" ;
	$ncb .= "</form>" ;
	return $ncb ;
}

if (isset($_POST['image']) and isset($_POST['article']) and isset($_POST['lang']))
{
	$article=urldecode($_POST['article']);
	$image=urldecode($_POST['image']);
	$article=str_replace("\\", "", $article);
	$image=str_replace("\\", "", $image);
	$lang=$_POST['lang'];
	
	// Create form
	$resume="Add image from http://tools.wikimedia.de/~emijrp/imagesforbio/";
	$position="right";
	switch($lang)
	{
		case 'ar': $resume="إضافة صورة من http://toolserver.org/~emijrp/imagesforbio/"; $position="left"; break;
		case 'bn': $resume="ছবি যোগ হয়েছে http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'bs': $resume="Dodajem sliku sa http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'cs': $resume="Přidaný obrázek pomocí http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'de': $resume="Bild hinzufügen mit http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'el': $resume="Προσθήκη εικόνας με το http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'en': $resume="Add image from http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'eo': $resume="Aldonis bildon per http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'es': $resume="Añado imagen desde http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'fa': $resume="افزودن نگاره به زندگی‌نامه http://toolserver.org/~emijrp/imagesforbio/"; $position="left"; break;
		case 'fi': $resume="Lisätty kuva työkalulla http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'fr': $resume="Ajout d'une image depuis http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'he': $resume="הוספת תמונה בעזרת http://toolserver.org/~emijrp/imagesforbio/"; $position="left"; break;
		case 'hr': $resume="Dodajem sliku sa http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'it': $resume="Aggiungi un'immagine usando http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'ja': $resume="http://toolserver.org/~emijrp/imagesforbio/ から画像を追加"; break;
		case 'nl': $resume="Afbeelding toegevoegd via http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'pl': $resume="Dodaj grafikę z tego źródła: http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'pt': $resume="Adicionada imagem usando http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'ru': $resume="Добавлено изображение. http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'sk': $resume="Pridaný obrázok pomocou http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'sl': $resume="Vključena bioslika s pomočjo http://tools.wikimedia.de/~emijrp/imagesforbio/"; break;
		case 'sr': $resume="додајем слику са http://toolserver.org/~emijrp/imagesforbio/"; break;
		case 'sv': $resume="Lägger till bild från http://toolserver.org/~emijrp/imagesforbio/"; break;
	}
	
	$text=leer("http://$lang.wikipedia.org/w/index.php?title=".str_replace(" ", "_", $article)."&action=raw", 'r');
	if (strlen($text)>0){
		if ($lang=='sl')
		{
			$text="{{bioslika|islike=$image|napis={{subst:PAGENAME}}}}\n$text";
		}else{
			$text="[[{{subst:ns:6}}:$image|thumb|$position|{{subst:PAGENAME}}]]\n$text";
		}
		
		$button = cGetEditButton ( $text , $article , $lang , "wikipedia" , $resume , "Click me if you have JavaScript disabled" , false , false , true , true ) ;
		$button = str_replace ( "type='submit'" , "type='submit' id='thebutton'" , $button ) ;

		// Output
		print "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"pl\" lang=\"pl\" dir=\"ltr\">\n<head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" /></head>\n";
		print "<body onload=\"document.getElementById('thebutton').click();\">" ;
		print $button ;
		print "<br/>(otherwise, wait a second or two...)<br/>Using some Magnus functions... Thank you Magnus" ;
		print "</body></html>" ;
	}else{
		print "http://$lang.wikipedia.org/w/index.php?title=".str_replace(" ", "_", $article)."&action=raw";
		print "error found";
	}
}

?>