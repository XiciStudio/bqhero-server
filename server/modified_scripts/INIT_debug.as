package
{
   import flash.external.ExternalInterface;

   public class INIT
   {

      public static const FPS:int = 30;

      public static var tag:Object = null;

      public static var errorB:Boolean = true;

      public function INIT()
      {
         super();
      }

      private static var _debugInited:Boolean = false;
      public static function debugLog(msg:String) : void
      {
         try
         {
            if (ExternalInterface.available)
            {
               ExternalInterface.call("console.log", "[SWF-INIT] " + msg);
            }
         }
         catch(e:*) {}
         trace("[SWF-INIT] " + msg);
      }

      public static function TRACE(obj0:*, tag0:Object = null) : void
      {
         if (!_debugInited)
         {
            _debugInited = true;
            debugLog("INIT.TRACE first called - SWF code is executing");
         }
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
         debugLog("showError: " + str0);
         if(errorB)
         {
            throw new Error(str0);
         }
      }

      public static function showErrorMust(str0:String, tag0:Object = null) : void
      {
         debugLog("showErrorMust: " + str0);
         throw new Error(str0);
      }
   }
}
