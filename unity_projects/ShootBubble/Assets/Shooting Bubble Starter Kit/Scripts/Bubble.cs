using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class Bubble : MonoBehaviour {

	public enum Type {
		None = 0,

        // normal bubbles
        Color1,
		Color2,
		Color3,
		Color4,
		Color5,
		Color6,
		Color7,
		Color8

	};
	
	public Type type {
		get;
		set;
	}
	
	public static Type CharToType(char ch)
	{
		if (ch >= '0' && ch <= '7')
		{
			return (Type)(ch - '0' + 1);
		}
		else
		{
			return Type.None;
		}
	}

    private static int maxNormalColorType = 8;

    public static Type GetRandomColor()
    {
        int rand = Random.Range(1, maxNormalColorType);
        return (Type)rand;
    }

    public static Type GetRandomColorOtherThan(Type exclude)
    {
        Type t = exclude;

        while (t == exclude)
            t = GetRandomColor();

        return t;
    }
    
    private static Type _lastOne = Type.None;
    private static Type _lastTwo = Type.None;
    
    public static Type GetRandomColorFromList(List<Type> all)
    {
    	if (all.Count > 0)
    	{
    		if (all.Count == 1)
    			return all[0];
    		
    		while (true)
    		{
		    	int index = Random.Range(0, all.Count);
		    	if (all[index] == _lastTwo && all[index] == _lastOne)
		    	{
		    		continue;
		    	}

				_lastTwo = _lastOne;
		    	_lastOne = all[index];
		    	
		    	return all[index];
    		}
    	}
    	
    	D.warn("[Bubble] Get none type...");
    	return Type.None;
    }
}
