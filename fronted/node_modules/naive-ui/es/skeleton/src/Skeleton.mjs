import { pxfy, repeat } from 'seemly';
import { computed, defineComponent, Fragment, h, mergeProps } from 'vue';
import { useConfig, useTheme } from "../../_mixins/index.mjs";
import { createKey, useHoudini } from "../../_utils/index.mjs";
import { skeletonLight } from "../styles/index.mjs";
import style from "./styles/index.cssr.mjs";
export const skeletonProps = Object.assign(Object.assign({}, useTheme.props), {
  text: Boolean,
  round: Boolean,
  circle: Boolean,
  height: [String, Number],
  width: [String, Number],
  size: String,
  repeat: {
    type: Number,
    default: 1
  },
  animated: {
    type: Boolean,
    default: true
  },
  sharp: {
    type: Boolean,
    default: true
  }
});
export default defineComponent({
  name: 'Skeleton',
  inheritAttrs: false,
  props: skeletonProps,
  setup(props) {
    useHoudini();
    const {
      mergedClsPrefixRef
    } = useConfig(props);
    const themeRef = useTheme('Skeleton', '-skeleton', style, skeletonLight, props, mergedClsPrefixRef);
    return {
      mergedClsPrefix: mergedClsPrefixRef,
      style: computed(() => {
        var _a, _b;
        const theme = themeRef.value;
        const {
          common: {
            cubicBezierEaseInOut
          }
        } = theme;
        const selfThemeVars = theme.self;
        const {
          color,
          colorEnd,
          borderRadius
        } = selfThemeVars;
        let sizeHeight;
        const {
          circle,
          sharp,
          round,
          width,
          height,
          size,
          text,
          animated
        } = props;
        if (size !== undefined) {
          sizeHeight = selfThemeVars[createKey('height', size)];
        }
        const mergedWidth = circle ? (_a = width !== null && width !== void 0 ? width : height) !== null && _a !== void 0 ? _a : sizeHeight : width;
        const mergedHeight = (_b = circle ? width !== null && width !== void 0 ? width : height : height) !== null && _b !== void 0 ? _b : sizeHeight;
        return {
          display: text ? 'inline-block' : '',
          verticalAlign: text ? '-0.125em' : '',
          borderRadius: circle ? '50%' : round ? '4096px' : sharp ? '' : borderRadius,
          width: typeof mergedWidth === 'number' ? pxfy(mergedWidth) : mergedWidth,
          height: typeof mergedHeight === 'number' ? pxfy(mergedHeight) : mergedHeight,
          animation: !animated ? 'none' : '',
          '--n-bezier': cubicBezierEaseInOut,
          '--n-color-start': color,
          '--n-color-end': colorEnd
        };
      })
    };
  },
  render() {
    const {
      repeat: repeatProp,
      style,
      mergedClsPrefix,
      $attrs
    } = this;
    // BUG:
    // Chrome devtools can't read the element
    // Maybe it's a bug of chrome
    const child = h('div', mergeProps({
      class: `${mergedClsPrefix}-skeleton`,
      style
    }, $attrs));
    if (repeatProp > 1) {
      return h(Fragment, null, repeat(repeatProp, null).map(_ => [child, '\n']));
    }
    return child;
  }
});