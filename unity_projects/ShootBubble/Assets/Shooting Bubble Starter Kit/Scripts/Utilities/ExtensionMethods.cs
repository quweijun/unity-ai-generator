using UnityEngine;
using System.Collections;

internal static class ExtensionMethods
{
    #region Transform

    public static void SetX(this Transform trans, float x)
    {
        trans.position = new Vector3(x, trans.position.y, trans.position.z);
    }

    public static void MoveBy(this Transform trans, float dx = 0.0f, float dy = 0.0f, float dz = 0.0f)
    {
        Vector3 position = trans.position;
        position.x += dx;
        position.y += dy;
        position.z += dz;
        trans.position = position;
    }
	
	public static void MoveBy(this Transform trans, Vector3 dv)
	{
		Vector3 position = trans.position;
		position.x += dv.x;
		position.y += dv.y;
		position.z += dv.z;
		trans.position = position;
	}
	
	public static void MoveBy(this Transform trans, Vector2 dv)
	{
		Vector3 position = trans.position;
		position.x += dv.x;
		position.y += dv.y;
		trans.position = position;
	}	
    #endregion


    #region 2D Toolkit

//    public static void SetText(this tk2dTextMesh mesh, string newText)
//    {
//        mesh.text = newText;
//        mesh.Commit();
//    }
//
//    public static void SetSpriteTo(this tk2dSprite sprite, string spriteName)
//    {
//        var spriteID = sprite.GetSpriteIdByName(spriteName);
//        sprite.spriteId = spriteID;
//    }

    #endregion

}
