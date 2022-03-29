from Setting import PlotSetting
import numpy as np

def plot_event(fig, axes, xlim):
    ax = fig.add_subplot(111, zorder=-1)
    ax.set_xlim(xlim[0], xlim[1])
    ax.spines.top.set_visible(False)
    ax.spines.right.set_visible(False)
    ax.spines.left.set_visible(False)
    ax.spines.bottom.set_position(("outward", 10))
    ax.get_shared_x_axes().join(ax, axes[0])
    ax.tick_params(left=False, labelleft=False, right=False)
    ax.set_ylim([0, 1])
    ax.plot([0, 0], [0, 1], color="k", alpha=0.3)
    return

def format_axis(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # remove ticks
    ax.tick_params(
        axis='y',          # changes apply to the y-axis
        which='both',      # both major and minor ticks are affected
        left=False,        # ticks along the left edge are off
        right=False,       # ticks along the right edge are off
        labelleft=False)   # labels along the left edge are off
    ax.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False) # labels along the bottom edge are off
    return

def plot_channels(line,axes,setting_instance:PlotSetting, prefix: str):
    channelmap= setting_instance.channelmap
    ylim=setting_instance.ylim
    xlim=setting_instance.xlim
    for ch_count,channel in enumerate(channelmap,1):
        wave=np.array(line[channel-1])
        i = ch_count-1
        # Set limits and labels
        axes[i].set_facecolor("#ffffff00")
        axes[i].set_xlim(xlim[0],xlim[1])
        axes[i].set_ylim(ylim[0],ylim[1])
        axes[i].set_ylabel(ch_count * 50, rotation=0, ha="right", va="center")
        # Plot base line
        axes[i].plot(xlim, [0, 0], color="k", alpha=0.3, linestyle="--")
        # Plot waveform
        time=range(xlim[0],xlim[1])
        axes[i].plot(time, wave, color="k", clip_on=False,)
        # Format spines and ticks
        if ch_count == len(channelmap):
            axes[i].spines['top'].set_visible(False)
            axes[i].spines['left'].set_visible(False)
            axes[i].spines['bottom'].set_visible(False)
            axes[i].spines['right'].set_position(("outward", 10))
            axes[i].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
            axes[i].yaxis.tick_right()
            axes[i].set_yticks([ylim[0], 0, ylim[1]])
            axes[i].set_yticklabels([ylim[0], f"0{prefix}V", ylim[1]])
        else:
            format_axis(axes[i])
    return

def get_timestamp_from_law_ch(single_channel_data,Th,isi,samplerate):
    timestamp=[]
    i=0
    while i<len(single_channel_data):
        if single_channel_data[i]>=Th:
            timestamp.append(i)
            i+=int(isi*samplerate)
        i+=1
    return timestamp




