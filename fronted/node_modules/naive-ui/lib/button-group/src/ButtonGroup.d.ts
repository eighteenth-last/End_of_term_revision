import type { PropType } from 'vue';
import type { ExtractPublicPropTypes } from '../../_utils';
import type { Size } from '../../button/src/interface';
export interface ButtonGroupInjection {
    size?: Size | undefined;
}
export declare const buttonGroupProps: {
    readonly size: {
        readonly type: PropType<Size | undefined>;
        readonly default: undefined;
    };
    readonly vertical: BooleanConstructor;
};
export type ButtonGroupProps = ExtractPublicPropTypes<typeof buttonGroupProps>;
declare const _default: import("vue").DefineComponent<import("vue").ExtractPropTypes<{
    readonly size: {
        readonly type: PropType<Size | undefined>;
        readonly default: undefined;
    };
    readonly vertical: BooleanConstructor;
}>, {
    rtlEnabled: import("vue").Ref<import("../../config-provider/src/internal-interface").RtlItem | undefined, import("../../config-provider/src/internal-interface").RtlItem | undefined> | undefined;
    mergedClsPrefix: import("vue").Ref<string, string>;
}, {}, {}, {}, import("vue").ComponentOptionsMixin, import("vue").ComponentOptionsMixin, {}, string, import("vue").PublicProps, Readonly<import("vue").ExtractPropTypes<{
    readonly size: {
        readonly type: PropType<Size | undefined>;
        readonly default: undefined;
    };
    readonly vertical: BooleanConstructor;
}>> & Readonly<{}>, {
    readonly size: Size | undefined;
    readonly vertical: boolean;
}, {}, {}, {}, string, import("vue").ComponentProvideOptions, true, {}, any>;
export default _default;
