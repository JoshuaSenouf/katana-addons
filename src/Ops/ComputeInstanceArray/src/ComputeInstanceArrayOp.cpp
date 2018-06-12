#include <iostream>
#include <string>
#include <cmath>
#include <algorithm>

#include <FnGeolib/op/FnGeolibOp.h>
#include <FnAttribute/FnAttribute.h>
#include <FnAttribute/FnGroupBuilder.h>
#include <FnGeolibServices/FnGeolibCookInterfaceUtilsService.h>

#include <OpenEXR/ImathVec.h>
#include <OpenEXR/ImathMatrix.h>


namespace {
class ComputeInstanceArrayOp : public Foundry::Katana::GeolibOp {
    public:
        static void setup(Foundry::Katana::GeolibSetupInterface& interface)
        {
            interface.setThreading(Foundry::Katana::GeolibSetupInterface::ThreadModeConcurrent);
        }

        static void cook(Foundry::Katana::GeolibCookInterface& interface)
        {
            FnAttribute::StringAttribute instanceArrayLocAttr = interface.getOpArg("instanceArrayLoc");

            if (!instanceArrayLocAttr.isValid())
            {
                return;
            }

            FnGeolibServices::FnGeolibCookInterfaceUtils::MatchesCELInfo matchInfo;
            FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchInfo, interface, instanceArrayLocAttr);

            if (!matchInfo.matches)
            {
                return;
            }

            FnAttribute::StringAttribute positionPrimvarAttr = interface.getOpArg("positionPrimvar");
            FnAttribute::StringAttribute rotationPrimvarAttr = interface.getOpArg("rotationPrimvar");
            FnAttribute::StringAttribute scalePrimvarAttr = interface.getOpArg("scalePrimvar");
            FnAttribute::StringAttribute protoIndicesPrimvarAttr = interface.getOpArg("protoIndicesPrimvar");

            FnAttribute::FloatAttribute positionAttr = interface.getAttr(
                "geometry.point." + positionPrimvarAttr.getValue());
            FnAttribute::FloatAttribute rotationAttr = interface.getAttr(
                "geometry.arbitrary." + rotationPrimvarAttr.getValue() + ".value");
            FnAttribute::FloatAttribute scaleAttr = interface.getAttr(
                "geometry.arbitrary." + scalePrimvarAttr.getValue() + ".value");
            FnAttribute::IntAttribute protoIndicesAttr = interface.getAttr(
                "geometry.arbitrary." + protoIndicesPrimvarAttr.getValue() + ".value");
            
            if (!positionAttr.isValid() ||
                !protoIndicesAttr.isValid())
            {
                std::cout << std::string("[PrmanInstanceArray] ERROR - ComputeInstanceArrayOp::cook() - The .abc file"
                " used for scattering the geometry does not contain all the necessary primvars! "
                "(\"" + positionPrimvarAttr.getValue() + "\" and \"" + protoIndicesPrimvarAttr.getValue() + "\","
                " as requested by user on the node)") << std::endl;
            
                return;
            }

            FnAttribute::FloatConstVector positionAttrVec = positionAttr.getNearestSample(0.0f);
            FnAttribute::FloatConstVector rotationAttrVec = rotationAttr.getNearestSample(0.0f);
            FnAttribute::FloatConstVector scaleAttrVec = scaleAttr.getNearestSample(0.0f);
            FnAttribute::IntConstVector protoIndicesAttrVec = protoIndicesAttr.getNearestSample(0.0f);

            std::vector<Imath::M44f> matricesVector;
            matricesVector.reserve(protoIndicesAttrVec.size());

            for (unsigned int instanceIdx = 0; instanceIdx < protoIndicesAttrVec.size(); ++instanceIdx)
            {
                Imath::M44f currentMatrix;

                currentMatrix.translate(Imath::V3f(positionAttrVec[instanceIdx * 3],
                    positionAttrVec[instanceIdx * 3 + 1],
                    positionAttrVec[instanceIdx * 3 + 2]));

                if (rotationAttr.isValid())
                {
                    currentMatrix.rotate(Imath::V3f(rotationAttrVec[instanceIdx * 3],
                        rotationAttrVec[instanceIdx * 3 + 1],
                        rotationAttrVec[instanceIdx * 3 + 2]));
                }

                if (scaleAttr.isValid())
                {
                    currentMatrix.scale(Imath::V3f(scaleAttrVec[instanceIdx * 3],
                        scaleAttrVec[instanceIdx * 3 + 1],
                        scaleAttrVec[instanceIdx * 3 + 2]));
                }

                matricesVector.push_back(currentMatrix);
            }

            interface.setAttr("geometry.instanceMatrix", FnAttribute::FloatAttribute(&matricesVector[0][0][0],
                matricesVector.size() * 16,
                16));
            interface.setAttr("geometry.instanceIndex", protoIndicesAttr);

            interface.stopChildTraversal();
        }
    private:
};

DEFINE_GEOLIBOP_PLUGIN(ComputeInstanceArrayOp)
}


void registerPlugins()
{
    REGISTER_PLUGIN(ComputeInstanceArrayOp, "ComputeInstanceArray", 0, 1);
}
