using UnityEngine;
using System.Collections;

/// <summary>
/// Rect with left-bottom coordinate.
/// </summary>
public class LBRect
{
    private float _left;
    private float _bottom;
    private float _width;
    private float _height;

    public LBRect(float left, float bottom, float width, float height)
    {
        _left = left;
        _bottom = bottom;
        _width = width;
        _height = height;
    }

    public float left
    {
        get
        {
            return _left;
        }
        set
        {
            _left = value;
        }
    }

    public float right
    {
        get
        {
            return _left + _width;
        }
        set
        {
            _width = value - _left;
        }
    }

    public float bottom
    {
        get
        {
            return _bottom;
        }
        set
        {
            _bottom = value;
        }
    }

    public float top
    {
        get
        {
            return _bottom + _height;
        }
        set
        {
            _height = value - _bottom;
        }
    }
	
	public float width
	{
		get
		{
			return _width;
		}
	}
	
	public float height
	{
		get
		{
			return _height;
		}
	}
	
    public bool IsInInnerOffset(float offset, float x, float y)
    {
        return x >= _left + offset && x <= _left + _width - offset && y >= _bottom + offset && y <= _bottom + _height - offset;
    }

    public bool IsInBounds(Vector3 hit)
    {
        float x = hit.x;
        float y = hit.y;

        return IsInInnerOffset(0, x, y);
    }
}
