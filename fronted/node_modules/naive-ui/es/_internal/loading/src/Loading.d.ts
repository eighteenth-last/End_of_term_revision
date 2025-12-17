import type { ExtractPublicPropTypes } from '../../../_utils';
declare const exposedLoadingProps: {
    strokeWidth: {
        type: NumberConstructor;
        default: number;
    };
    stroke: {
        type: StringConstructor;
        default: undefined;
    };
};
export type BaseLoadingExposedProps = ExtractPublicPropTypes<typeof exposedLoadingProps>;
declare const _default: import("vue").DefineComponent<import("vue").ExtractPropTypes<{
    strokeWidth: {
        type: NumberConstructor;
        default: number;
    };
    stroke: {
        type: StringConstructor;
        default: undefined;
    };
    clsPrefix: {
        type: StringConstructor;
        required: true;
    };
    show: {
        type: BooleanConstructor;
        default: boolean;
    };
    scale: {
        type: NumberConstructor;
        default: number;
    };
    radius: {
        type: NumberConstructor;
        default: number;
    };
}>, void, {}, {}, {}, import("vue").ComponentOptionsMixin, import("vue").ComponentOptionsMixin, {}, string, import("vue").PublicProps, Readonly<import("vue").ExtractPropTypes<{
    strokeWidth: {
        type: NumberConstructor;
        default: number;
    };
    stroke: {
        type: StringConstructor;
        default: undefined;
    };
    clsPrefix: {
        type: StringConstructor;
        required: true;
    };
    show: {
        type: BooleanConstructor;
        default: boolean;
    };
    scale: {
        type: NumberConstructor;
        default: number;
    };
    radius: {
        type: NumberConstructor;
        default: number;
    };
}>> & Readonly<{}>, {
    show: boolean;
    stroke: string;
    strokeWidth: number;
    scale: number;
    radius: number;
}, {}, {}, {}, string, import("vue").ComponentProvideOptions, true, {}, any>;
export default _default;
