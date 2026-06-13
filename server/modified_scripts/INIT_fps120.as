package
{
   public class INIT
   {

      public static var FPS:int = 30;

      public static var tag:Object = null;

      public static var errorB:Boolean = true;

      public function INIT()
      {
         super();
      }

      public static function TRACE(obj0:*, tag0:Object = null) : void
      {
         if(errorB)
         {
            if(tag0 == tag || !tag0)
            {
               trace(obj0);
            }
         }
      }

      public static function tempTrace(obj0:*) : void
      {
         TRACE(obj0);
      }

      public static function addText(v0:String) : void
      {
      }

      public static function showError(str0:String, tag0:Object = null) : void
      {
         if(errorB)
         {
            throw new Error(str0);
         }
      }

      public static function showErrorMust(str0:String, tag0:Object = null) : void
      {
         throw new Error(str0);
      }
   }
}
