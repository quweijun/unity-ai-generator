#define SOUND_STICK_TO_CAMERA

using UnityEngine;
using System.Collections;
using System.Collections.Generic;

// Adapted from http://dirigiballers.blogspot.com/2013/03/unity-c-audiomanager-tutorial-part-4.html
// we can actually add voice over or fade in/out in this class, but our usage is rather simple. so keep it simple!

public class AudioManager : Singleton<AudioManager>
{
	private class ClipInfo
	{
		public AudioSource 	source  		{ get; set; }
		public float 		defaultVolume 	{ get; set; }
	}
	
	private List<ClipInfo> 	_activeAudio;
	private AudioSource 	_activeMusic;

	protected AudioManager()
	{
	}

	public void Awake()
	{
		D.log("[AudioManager] initializing");

		_activeAudio = new List<ClipInfo>();

		transform.position = Vector3.zero;
	}
	
	public AudioSource Play(AudioClip clip)
	{
		return this.Play(clip, this.transform, 1.0f, false);
	}
	
	private AudioSource Play(AudioClip clip, Transform emitter, float volume, bool isLoop)
	{
		// create an empty game object
		GameObject soundObj = new GameObject("Audio: " + clip.name);
		soundObj.transform.position = emitter.position;
		soundObj.transform.parent = emitter;

		// create the source
		AudioSource source = soundObj.AddComponent<AudioSource>();
		SetSource(ref source, clip, volume, isLoop);
		source.Play();
		Destroy(soundObj, clip.length);

		// set the source as active
		_activeAudio.Add(new ClipInfo { source = source, defaultVolume = volume });
		return source;
	}
	
	public AudioSource Play(AudioClip clip, Transform emitter, float volume)
	{
#if SOUND_STICK_TO_CAMERA
		var source = Play(clip, transform, volume, false);
#else
		var source = Play(clip, emitter, volume, false);
#endif
		return source;
	}
	
	public AudioSource PlayLoop(AudioClip clip, Transform emitter, float volume)
	{
#if SOUND_STICK_TO_CAMERA
		var source = Play(clip, transform, volume, true);
#else
		var source = Play(clip, emitter, volume, true);
#endif
		return source;
	}

	public AudioSource PlayMusic(AudioClip music, float volume)
	{
		_activeMusic = PlayLoop(music, transform, volume);
		return _activeMusic;
	}

	public void Stop(AudioSource toStop)
	{
		try
		{
			Destroy(_activeAudio.Find(s => s.source == toStop).source.gameObject);
		}
		catch
		{
			D.log("[AudioManager] Error trying to stop audio source " + toStop);
		}
	}
	
	public void PauseFX()
	{
		foreach (var audioClip in _activeAudio)
		{
			try
			{
				if (audioClip.source != _activeMusic)
					audioClip.source.Pause();
			}
			catch
			{
				continue;
			}
		}
	}

	public void UnpauseFX()
	{
		foreach (var audioClip in _activeAudio)
		{
			try
			{
				if (audioClip.source != _activeMusic && !audioClip.source.isPlaying)
					audioClip.source.Play();
			}
			catch
			{
				continue;
			}
		}
	}
	
	public void PauseMusic()
	{
		if (_activeMusic)
			_activeMusic.Pause();
	}

	public void UnpauseMusic()
	{
		if (_activeMusic && !_activeMusic.isPlaying)
			_activeMusic.Play();
	}

	public void Update()
	{
		UpdateActiveAudio();
	}

	private void SetSource(ref AudioSource source, AudioClip clip, float volume, bool isLoop)
	{
		source.rolloffMode 	= AudioRolloffMode.Logarithmic;
		source.dopplerLevel = 0.2f;
		source.minDistance	= 150.0f;
		source.maxDistance	= 1500.0f;
		source.clip			= clip;
		source.loop			= isLoop;
		source.volume 		= volume;
	}

	private void UpdateActiveAudio()
	{
		var toRemove = new List<ClipInfo>();
		
		try
		{
			foreach (var audioClip in _activeAudio)
			{
				if (!audioClip.source)
					toRemove.Add(audioClip);
			}
		}
		catch
		{
			D.log("[AudioManager] Error updating active audio clips");
		}

		// cleanups
		foreach (var audioClip in toRemove)
			_activeAudio.Remove(audioClip);
	}
}
