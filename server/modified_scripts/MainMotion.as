package com.sounto.motion
{
   import com.sounto.math.Maths;
   import dataAll.level.define.mapRect.MapRect;
   
   public class MainMotion implements IO_Motion
   {

      public static const SPEED_SCALE:Number = 1.0;

      public var enabled:Boolean = true;
      
      public var x:Number = 0;
      
      public var y:Number = 0;
      
      protected var beforeX:Number = 0;
      
      protected var beforeY:Number = 0;
      
      public var vx:Number = 0;
      
      public var vy:Number = 0;
      
      public function MainMotion()
      {
         super();
      }
      
      public static function countGap(mot1:MainMotion, mot2:MainMotion) : Number
      {
         return Maths.Long(mot1.x - mot2.x,mot1.y - mot2.y);
      }
      
      public static function countRa(mot1:MainMotion, mot2:MainMotion) : Number
      {
         return Math.atan2(mot2.y - mot1.y,mot2.x - mot1.x);
      }
      
      public function getBeforeGap() : Number
      {
         return Maths.Long(this.x - this.beforeX,this.y - this.beforeY);
      }
      
      public function getMapRect() : MapRect
      {
         var rect0:MapRect = new MapRect();
         rect0.x = this.x;
         rect0.y = this.y;
         return rect0;
      }
      
      public function setX(v0:Number) : void
      {
         this.x = v0;
      }
      
      public function setY(v0:Number) : void
      {
         this.y = v0;
      }
      
      public function getX() : Number
      {
         return this.x;
      }
      
      public function getY() : Number
      {
         return this.y;
      }
   }
}

